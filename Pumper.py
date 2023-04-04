from binance.client import Client
import numpy as np
import pandas as pd
import talib
import Telegram_bot as Tb
import time
import requests

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
    slope = (end_price - start_price) / (high - low)
    intercept = end_price - slope * high
    
    # Agrega las líneas del canal al DataFrame
    fib_df['upper'] = slope * fib_df['price'] + intercept
    fib_df['lower'] = -slope * fib_df['price'] + 2 * end_price - intercept
    
    return fib_df
       
def calculate_macd_signal(prices):
    macd, signal, hist = talib.MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9)
    return macd, signal, hist

while True:
    # Espera hasta que sea el comienzo de una nueva hora
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)   
  
    for symbol in symbols:
    # Obtén los datos de precios históricos para el símbolo
      klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE)
      
      prices = np.array([float(kline[2]) for kline in klines])
    
      # Calcula el precio máximo y mínimo
      high = np.max(prices)
      low = np.min(prices)
    
      # Genera los canales de Fibonacci
      fib_df = fibonacci_channel(high, low)
    
      # Calcula el MACD y Signal
      macd, signal, hist = calculate_macd_signal(prices)
    
      # Calcula el indicador RSI
      rsi = talib.RSI(prices, timeperiod=14)
      
      # Obtener el order book del symbolo
      order_book = client.futures_order_book(symbol=symbol)
      # Obtener el precio de la apuesta mayor
      best_bid_price = float(order_book['bids'][0][0])
      
       # Calcula el valor de la EMA de 200 períodos
      ema = talib.EMA(prices, timeperiod=200)[-1]
    
    
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
      # Chequea si el precio es mayor al canal más alto de Fibonacci y si hay un cruce bajista de MACD y Signal o un cruce bajista del RSI y el nivel 70
      
      # Contra-Tendencia (Cierre de la tendencia)
      if prices[-1] > fib_df['upper'].iloc[-1] and (rsi[-2] > 70 and rsi[-1] < 70):
        Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {prices[-1]}\n💰 P-Max: {round(fib_df['upper'].iloc[-1],4)} \n best_bid: {best_bid_price}\n Contratendencia ")
        requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=CONTRASHORT)   
      if prices[-1] < fib_df['lower'].iloc[-1] and (rsi[-2] < 30 and rsi[-1] > 30):
        Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {prices[-1]}\n💰 P-Min: {round(fib_df['lower'].iloc[-1],4)}\n best_bid: {best_bid_price}\n Contratendencia")
        requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=CONTRALONG) 
        
      #Tendencia FISHING
      if ema > prices[-1] < fib_df['lower'].iloc[-1] and (macd[-1] < signal[-1] and macd[-2] > signal[-2]):
        Tb.telegram_send_message(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {prices[-1]}\n💰 P-Min: {round(fib_df['lower'].iloc[-1],4)}\n🎣 Fishing Pisha") 
        requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT) 
      if ema < prices[-1] > fib_df['upper'].iloc[-1] and (macd[-1] > signal[-1] and macd[-2] < signal[-2]):
        Tb.telegram_send_message(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {prices[-1]}\n💰 P-Max: {round(fib_df['upper'].iloc[-1],4)}\n🎣 Fishing Pisha") 
        requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
        
      # Imprime los resultados
      print(symbol)
      print(ema)

   
