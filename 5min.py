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
       
def calculate_adx(prices_high, prices_low, prices_close):
    adx = talib.ADX(prices_high, prices_low, prices_close, timeperiod=14)
    return adx 


def calculate_bbands(prices):
    upper, middle, lower = talib.BBANDS(prices, timeperiod=20, nbdevup=2, nbdevdn=2, matype=talib.MA_Type.SMA)
    return upper, middle, lower  


  
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
         
         
      # Calcula el indicador RSI
      rsi = talib.RSI(prices, timeperiod=14)
             
      # Calcula el indicador ADX
      adx = calculate_adx(prices_high, prices_low, prices_close)
      
       # Calcula Bandas de Bollinger
      upperband, middleband, lowerband = calculate_bbands(prices_close)
      
      depth = 5
      order_book = client.futures_order_book(symbol=symbol, limit=depth)

        # Calcula el desequilibrio de ask y bid
      bids = order_book['bids']
      asks = order_book['asks']
      bid_sum = sum([float(bid[1]) for bid in bids])
      ask_sum = sum([float(ask[1]) for ask in asks])

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
        "price": prices_close
        }
        }
     
      # Chequea si el precio es mayor al canal más alto de Fibonacci y si hay un cruce bajista de MACD y Signal o un cruce bajista del RSI y el nivel 70
      
       # TENDENCIA ALCISTA:
      if (diff[-2] > 1) and (prices_close[-2] > upperband[-2]) and (imbalance >= 0.5) and (adx[-2] <= 20):
          Tb.telegram_send_message(f"🎣 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {prices_close[-2]}\n⛳️ IMB : {round(imbalance,2)} \n(🎣 Fishing Pisha")
          requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
      elif (diff[-2] > 1) and (prices_close[-2] > upperband[-2]) and (rsi[-2] >= 75) and (imbalance <= -0.6): 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Cambio: % {round(diff[-2],2)} \n💵 Precio: {prices_close[-2]}\n⛳️ IMB : {round(imbalance,2)}")
          requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CONTRASHORT)   
        
        # TENDENCIA BAJISTA:
      if (diff[-2] > 1) and (prices_close[-2] < lowerband[-2]) and (imbalance <= -0.5) and (adx[-2] >= 45):
          Tb.telegram_send_message(f"🎣 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {prices_close[-2]}\n⛳️ IMB : {round(imbalance,2)} \n🎣 Fishing Pisha")
          requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT)
      elif (diff[-2] > 1) and (prices_close[-2] < lowerband[-2]) and (rsi[-2] <= 25) and (imbalance >= 0.6): 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Cambio: % {round(diff[-2],2)} \n💵 Precio: {prices_close[-2]}\n⛳️ IMB : {round(imbalance,2)}")
          requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=CONTRALONG)   
        
         #Cruce de EMAS + FIBO:
       
      if (imbalance >  0.9):
        Tb.telegram_canal_prueba(f"🐬 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {prices_close[-2]}\nIMB : {round(imbalance,2)} \n🐬 Delfin")  
        #requests.post('https://hook.finandy.com/9nQNB3NdMGaoK-xWqVUK', json=DELFINLONG) 
        
      if (imbalance <  -0.9):
        Tb.telegram_canal_prueba(f"🐬 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {prices_close[-2]}\nIMB : {round(imbalance,2)} \n🐬 Delfin")
      
        # Imprime los resultados

      print(symbol)
