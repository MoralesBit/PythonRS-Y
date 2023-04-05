from binance.client import Client
import numpy as np
import pandas as pd
import talib
import Telegram_bot as Tb
import time
import requests
from binance.exceptions import BinanceAPIException

api_key = 'TU_API_KEY'
api_secret = 'TU_API_SECRET'

client = Client(api_key, api_secret)

futures_info = client.futures_exchange_info()
symbols = [symbol['symbol'] for symbol in futures_info['symbols']]

# Crea una función para generar los canales de Fibonacci:
def fibonacci_channel(high, low):
      
    # Calcula los niveles de Fibonacci
    fib_levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
    fib_values = [(high - low) * level + low for level in fib_levels]
    
    # Crea un DataFrame con los niveles de Fibonacci
    fib_df = pd.DataFrame(fib_values, columns=['price'])
    fib_df['level'] = fib_levels
    
    # Calcula los puntos de inicio y fin del canal
    start_price = fib_values[2]
    end_price = fib_values[5]
    
    # Calcula la pendiente y la intersección de la línea del canal
    try:
        slope = (end_price - start_price) / (high - low)
    except ZeroDivisionError:
       print("No se ha podido realizar la división")
       
    intercept = end_price - slope * high
    
    # Agrega las líneas del canal al DataFrame
    fib_df['upper'] = slope * fib_df['price'] + intercept
    fib_df['lower'] = -slope * fib_df['price'] + 2 * end_price - intercept
    
    return fib_df
       
def calculate_macd_signal(prices):
    macd, signal, hist = talib.MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9)
    return macd, signal, hist

def calculate_adx(high, low, close):
    adx = talib.ADX(high, low, close, timeperiod=14)
    return adx 

def calculate_cci(high, low, close):
    cci = talib.CCI(high, low, close, timeperiod=58)
    return cci

def calculate_des(prices):
    des = (3)*(talib.STDDEV(prices,200))   
    return des 

while True:
    # Espera hasta que sea el comienzo de una nueva hora
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)   
  
    for symbol in symbols:
         
    # Obtén los datos de precios históricos para el símbolo
      klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE)
          
      prices = np.array([float(kline[2]) for kline in klines])
      prices_high = np.array([float(kline[3]) for kline in klines])
      prices_low = np.array([float(kline[4]) for kline in klines])
      prices_close = np.array([float(kline[5]) for kline in klines])
    
      # Calcula el precio máximo y mínimo
      high = np.max(prices)
      low = np.min(prices)
    
      # Genera los canales de Fibonacci
      fib_df = fibonacci_channel(high, low)
          
      # Calcula el MACD y Signal
      macd, signal, hist = calculate_macd_signal(prices)
    
      # Calcula el indicador RSI
      rsi = talib.RSI(prices, timeperiod=14)
             
      # Calcula el valor de la EMA de 200 períodos
      ema = talib.EMA(prices, timeperiod=200)[-1]
      
      # Calcula el indicador ADX
      adx = calculate_adx(prices_high, prices_low, prices_close)
      
      # Calcula el indicador cci
      cci = calculate_cci(prices_high, prices_low, prices_close)  
      
      # Calcula el indicador Desviacion Estandar
      dev = calculate_des(prices)
      
      basis = talib.WMA(prices_close, timeperiod=200)
      fu1 = basis + (1*dev)
      fd1 = basis -(1*dev) 
    
      # DATOS FNDY
      FISHINGSHORT = {
    "name": "SHORT-MINIFISH",
    "secret": "azsdb9x719",
    "side": "sell",
    "symbol": symbol
    }
      FISHINGLONG = {
    "name": "LONG-MINIFISH",
    "secret": "0kivpja7tz89",
    "side": "buy",
    "symbol": symbol
    }
    
      CONTRASHORT = {
    "name": "SHORT-MINIFISH",
    "secret": "hgw3399vhh",
    "side": "sell",
    "symbol": symbol
    }
      CONTRALONG = {
    "name": "LONG-MINIFISH",
    "secret": "xjth0i3qgb",
    "side": "buy",
    "symbol": symbol
    }  
    
      VIEWSHORT = {
    "name": "VIEW SHOR",
    "secret": "w48ulz23f6",
    "side": "sell",
    "symbol": symbol
    }
      VIEWLONG = {
    "name": "VIEW LONG",
    "secret": "xxuxkqf0gpj",
    "side": "buy",
    "symbol": symbol
    }
     
      # Chequea si el precio es mayor al canal más alto de Fibonacci y si hay un cruce bajista de MACD y Signal o un cruce bajista del RSI y el nivel 70
      
      # Contra-Tendencia (Cierre de la tendencia)
      if (prices[-1] > fib_df['upper'].iloc[-1]) and (rsi[-2] > 70 and rsi[-1] < 70) and (adx[-1] > 20) and (adx[-1] < 40):
        Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {prices[-1]}\n💰 P-Max: {round(fib_df['upper'].iloc[-1],4)}\n Contratendencia ")
        requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=CONTRASHORT)   
      if (prices[-1] < fib_df['lower'].iloc[-1]) and (rsi[-2] < 30 and rsi[-1] > 30) and (adx[-1] > 20) and (adx[-1] < 40):
        Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {prices[-1]}\n💰 P-Min: {round(fib_df['lower'].iloc[-1],4)}\n Contratendencia")
        requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=CONTRALONG) 
        
      #Tendencia FISHING
      if (ema > prices[-1] < fib_df['lower'].iloc[-1]) and (macd[-1] < signal[-1] and macd[-2] > signal[-2]) and (adx[-1] > 20) and (adx[-1] < 40):
        Tb.telegram_send_message(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {prices[-1]}\n💰 P-Min: {round(fib_df['lower'].iloc[-1],4)}\n🎣 Fishing Pisha") 
        requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT) 
      if (ema < prices[-1] > fib_df['upper'].iloc[-1]) and (macd[-1] > signal[-1] and macd[-2] < signal[-2]) and (adx[-1] > 20) and (adx[-1] < 40):
        Tb.telegram_send_message(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {prices[-1]}\n💰 P-Max: {round(fib_df['upper'].iloc[-1],4)}\n🎣 Fishing Pisha") 
        requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
        
      #Tradingview FIBO + RSI
      if (prices_high[-2] > fu1[-2]) and (rsi[-2] > 70):
        Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {prices[-1]}\n💰 P-Min: {round(fib_df['lower'].iloc[-1],4)}\n Tradingview") 
        requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=VIEWSHORT) 
      if (prices_low[-2] < fd1[-2]) and (rsi[-2] < 30):
        Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {prices[-1]}\n💰 P-Max: {round(fib_df['upper'].iloc[-1],4)}\n Tradingview") 
        requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=VIEWLONG)   
        
      # Imprime los resultados
      print(symbol)
      
      

   
