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
       
def calculate_adx(prices_high, prices_low, prices):
    adx = talib.ADX(prices_high, prices_low, prices, timeperiod=14)
    return adx 


def calculate_bbands(prices):
    upper, middle, lower = talib.BBANDS(prices, timeperiod=20, nbdevup=2, nbdevdn=2, matype=talib.MA_Type.SMA)
    return upper, middle, lower  

def calculate_est( prices_high, prices_low, prices ):
    slowk, slowd = talib.STOCH(prices_high, prices_low, prices, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
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
      
      diff = abs((prices_high / prices_low -1) * 100) 
      
      #Cruce de EMAS
      ema_13 = talib.EMA(prices, timeperiod=13)
      ema_100 = talib.EMA(prices, timeperiod=100)
      ema_200 = talib.EMA(prices, timeperiod=200) 
                  
      # Calcula el indicador RSI
      rsi = talib.RSI(prices, timeperiod=14)
             
      # Calcula el indicador ADX
      adx = calculate_adx(prices_high, prices_low, prices)
      
       # Calcula Bandas de Bollinger
      upperband, middleband, lowerband = calculate_bbands(prices_close)
      
      #Calcula Slok SloD
    
      slowk, slowd = calculate_est(prices_high, prices_low, prices)
      
      
      # Calcula el precio máximo y mínimo
      high = np.max(prices)
      low = np.min(prices)
      # Genera los canales de Fibonacci
      diference = high - low
      fourth_level = high -  diference*0.618
      
      #Imbalance
      depth = 10

      response = requests.get(f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit={depth}').json()
      if 'bids' in response:
          bid_sum = sum([float(bid[1]) for bid in response['bids']])
      else:
          bid_sum = 0.0

      if 'asks' in response:
          ask_sum = sum([float(ask[1]) for ask in response['asks']])
      else:
         ask_sum = 0.0

      if bid_sum + ask_sum > 0:
          imbalance = (ask_sum - bid_sum) / (bid_sum + ask_sum)
      else:
          imbalance = 0.0    
      
           # DATOS FNDY
      FISHINGSHORT = {
        "name": "FISHING SHORT",
        "secret": "azsdb9x719",
        "side": "sell",
        "symbol": symbol,
        "open": {
        "price": prices_close
        }
        }
        
      FISHINGLONG = {
        "name": "FISHING LONG",
        "secret": "0kivpja7tz89",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": prices_close
        }
        }
    
      BOUNCYSHORT = {
        "name": "BOUNCY SHORT",
        "secret": "hgw3399vhh",
        "side": "sell",
        "symbol": symbol,
         "open": {
        "price": prices_close
        }
        }
        
      BOUNCYLONG = {
        "name": "BOUNCY LONG",
        "secret": "xjth0i3qgb",
        "side": "buy",
        "symbol": symbol,
         "open": {
        "price": prices_close
        }
        }  
    
      CONTRASHORT = {
        "name": "CONTRA SHORT",
        "secret": "w48ulz23f6",
        "side": "sell",
        "symbol": symbol,
        "open": {
        "price": prices_close
        }
        }
      CONTRALONG = {
        "name": "CONTRA LONG",
        "secret": "xxuxkqf0gpj",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": prices_close
        }
        }
        
      DELFINLONG = {
        "name": "DELFIN LONG",
        "secret": "an0rvlxehbn",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": ema_13[-2]
        }
        }
     
      # Chequea si el precio es mayor al canal más alto de Fibonacci y si hay un cruce bajista de MACD y Signal o un cruce bajista del RSI y el nivel 70
      
       # TENDENCIA ALCISTA:
      if (ema_200[-2] < prices[-2]) and (ema_13[-3] <  ema_100[-3]) and (ema_13[-2] > ema_100[-2]) and (imbalance > -0.15):
          Tb.telegram_send_message(f"🎣 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {prices_close[-2]}\n⛳️ IMB : {round(imbalance,2)} \n {ema_200[-2]}\n 🎣 Fishing Pisha")
          requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
      if (diff[-2] > 1) and (prices[-2] > upperband[-2]) and (rsi[-2] >= 70) and (imbalance <= -0.6): 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Cambio: % {round(diff[-2],2)} \n💵 Precio: {prices[-2]}\n⛳️ IMB : {round(imbalance,2)}")
          requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CONTRASHORT)   
        
        # TENDENCIA BAJISTA:
      if (ema_200[-2] > prices[-2]) and (ema_13[-3] >  ema_100[-3]) and (ema_13[-2] < ema_100[-2]) and (imbalance < 0.15):
          Tb.telegram_send_message(f"🎣 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {prices_close[-2]}\n⛳️ IMB : {round(imbalance,2)}\n {ema_200[-2]} \n🎣 Fishing Pisha")
          requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT)
      if (diff[-2] > 1) and (prices[-2] < lowerband[-2]) and (rsi[-2] <= 30) and (imbalance >= 0.6): 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Cambio: % {round(diff[-2],2)} \n💵 Precio: {prices[-2]}\n⛳️ IMB : {round(imbalance,2)}")
          requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=CONTRALONG)   
        
         #Cruce de EMAS + FIBO:
       
      if (imbalance >  0.7) and (prices[-3] < fourth_level) and (prices[-2] > fourth_level) :
        Tb.telegram_canal_prueba(f"🐬 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {prices[-2]}\nIMB : {round(imbalance,2)} \n🐬 Delfin")  
        #requests.post('https://hook.finandy.com/9nQNB3NdMGaoK-xWqVUK', json=DELFINLONG) 
        
      if (imbalance <  -0.7) and (prices[-3] > fourth_level) and (prices[-2] < fourth_level) :
        Tb.telegram_canal_prueba(f"🐬 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {prices[-2]}\nIMB : {round(imbalance,2)} \n🐬 Delfin")
        
       #Cruve de ema normal en el mismo sentido del cruce pero lanzando la orden de compra en la ema13:
      if (ema_13[-3] <  ema_100[-3]) and (ema_13[-2] > ema_100[-2]) and (imbalance > -0.15):
        Tb.telegram_canal_prueba(f"EMA normal {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {prices[-2]}\nIMB : {round(imbalance,2)} \nEMA en tendencia")     
          
        requests.post('https://hook.finandy.com/9nQNB3NdMGaoK-xWqVUK', json=DELFINLONG) 
        
      if (ema_13[-3] >  ema_100[-3]) and (ema_13[-2] < ema_100[-2]) and (imbalance < 0.15):
         Tb.telegram_canal_prueba(f"EMA normal {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {prices[-2]}\nIMB : {round(imbalance,2)} \nEMA en tendencia") 
      
        # Imprime los resultados

      print(symbol)     
