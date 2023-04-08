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
       
def calculate_macd_signal(prices):
    macd, signal, hist = talib.MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9)
    return macd, signal, hist

def calculate_adx(prices_high, prices_low, prices_close):
    adx = talib.ADX(prices_high, prices_low, prices_close, timeperiod=14)
    return adx 

def calculate_des(prices):
    des = (talib.STDDEV(prices,20))   
    return des 

def calculate_bbands(prices):
    upper, middle, lower = talib.BBANDS(prices, timeperiod=20, nbdevup=2, nbdevdn=2, matype=talib.MA_Type.SMA)
    return upper, middle, lower  

def calculate_est( prices_high, prices_low, prices_close ):
    slowk, slowd = talib.STOCH(prices_high, prices_low, prices_close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    return slowk, slowd
  
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
      
      # Calculate Fibonacci
      basis = talib.WMA(prices_close, timeperiod=20)
      dev = (3) * talib.STDDEV(prices_close, timeperiod=20)
      fu764 = basis + (0.001 * 764 * dev)
      fu5 = basis + (0.001 * 500 * dev)
      fu1 = basis + (1 * dev)      
      fd764 = basis - (0.001 * 764 * dev)
      fd5 = basis - (0.001 * 500 * dev)
      fd1 = basis - (1 * dev)
         
      # Genera los canales de Fibonacci
      diference = high - low
      
      first_level = high -  diference*0.236
      secound_level = high -  diference* 0.382
      third_level =high -  diference*0.5
      fourth_level = high -  diference*0.618
      fifth_level = high - diference * 1
      sixth_level = high - diference * 0
      seven_level = high - diference * 0.886
          
      # Calcula el MACD y Signal
      macd, signal, hist = calculate_macd_signal(prices)
    
      # Calcula el indicador RSI
      rsi = talib.RSI(prices_close, timeperiod=14)
             
      # Calcula el valor de la EMA de 200 períodos
      ema = talib.EMA(prices, timeperiod=200)
      
      # Calcula el indicador ADX
      adx = calculate_adx(prices_high, prices_low, prices_close)
      
      # Calcula el indicador Desviacion Estandar
      dev = calculate_des(prices_close)
      
      # Calcula Bandas de Bollinger
      upper, middle, lower = calculate_bbands(prices_close)     
      
      #Calcula Slok SloD
    
      slowk, slowd = calculate_est(prices_high, prices_low, prices_close)
    
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
      if (prices_close[-2] > sixth_level[-2]) and (rsi[-3] > 70) and (rsi[-2] <= 70) :
        Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {prices[-1]}\n💰F-1 : {sixth_level}\nRSI : {rsi[-2]}\n Contratendencia")
        requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=CONTRASHORT)   
      if (prices_close[-2] < fifth_level[-2]) and (rsi[-3] < 30) and (rsi[-2] >= 30) : 
        Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {prices[-1]}\n💰F-0 : {fifth_level}\nRSI : {rsi[-2]}\n Contratendencia")
        requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=CONTRALONG) 
        
      #Tendencia FISHING
      if (ema[-2] > prices_close[-2]) and (prices_close[-2] < fd5[-2]):
        Tb.telegram_send_message(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {prices[-1]}\n fd5 : {fd5}\n🎣 Fishing Pisha") 
        requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT) 
      if (ema[-2] < prices_close[-2]) and (prices_close[-2] > fu5[-2]):
        Tb.telegram_send_message(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {prices[-1]}\n fu5 : {fu5}\n🎣 Fishing Pisha") 
        requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
        
      #Tendencia view
      if (prices_high[-2] > fd1[-2]) and (rsi[-2] > 70):
        Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {prices[-1]}\n💰 fd764: {fd764} \n fd1 : {fd1} TW") 
        requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=VIEWSHORT) 
      if (prices_low[-2] > fu1[-2]) and (rsi[-2] < 30):
        Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {prices[-1]}\n💰 fu764: {fu764} \n fu1 : {fu1} TW") 
        requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=VIEWLONG) 
        
      
      # Imprime los resultados

      print(symbol)
