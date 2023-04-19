import requests
import pandas as pd
import numpy as np
import talib as ta
import Telegram_bot as Tb
import schedule as schedule
import time as ti
import json

api_key = 'TU_API_KEY'
api_secret = 'TU_API_SECRET'

futures_info_url = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
response = requests.get(futures_info_url).json()
symbols = [
    symbol['symbol'] for symbol in response['symbols']
    if symbol['status'] == "TRADING"
  ]

def indicator(symbol):
    
  url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=5m&startTime=2 days ago UTC+1&limit=500'
  response = requests.get(url).json()
  df = pd.DataFrame(response, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
  df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
  df = df.set_index('Open time')
  if not df.empty:

    upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                                timeperiod=20,
                                                nbdevup=2,
                                                nbdevdn=2,
                                                matype=0)
    df['upperband'] = upperband
    df['middleband'] = middleband
    df['lowerband'] = lowerband
       
    df['rsi'] = ta.RSI(df["Close"], timeperiod=14)
    adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
         
    Close = float(df['Close'][-2])
    Close_3 = float(df['Close'][-3])
    Open = float(df['Open'][-2])
    High = float(df['High'][-2])
    Low = float(df['Low'][-2])
    diff = abs((High / Low -1) * 100)
    rsi = df['rsi'][-2]
        
    df['EMA13'] = (df['Close'].ewm(13).mean())
    df['EMA200'] = (df['Close'].ewm(200).mean())
    df['EMA100'] = (df['Close'].ewm(100).mean())
    df['ema_cross'] = np.where(df['EMA13'] > df['EMA100'], np.where(df['EMA13'][-1] <= df['EMA100'][-1],1,0), np.where(df['EMA13'][-1] >= df['EMA100'][-1], -1, 0))
    
    ema_cross = df['ema_cross'][-2]
     

    # Calcular los niveles Fibonacci
    precio_high = float(max(df['Close']))
    precio_low = float(min(df['Close']))
    diff_precio = precio_high - precio_low
    nivel_786 = precio_high - (0.786)*(diff_precio)
    nivel_382 = precio_high - (0.382)*(diff_precio)
    
    #imbalaance
    depth = 5

    url = f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit={depth}'
    response = requests.get(url).json()
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
        "price": Close
        }
        }
        
  FISHINGLONG = {
        "name": "FISHING LONG",
        "secret": "0kivpja7tz89",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": Close
        }
        }
    
  BOUNCYSHORT = {
        "name": "BOUNCY SHORT",
        "secret": "hgw3399vhh",
        "side": "sell",
        "symbol": symbol,
         "open": {
        "price": Close
        }
        }
        
  BOUNCYLONG = {
        "name": "BOUNCY LONG",
        "secret": "xjth0i3qgb",
        "side": "buy",
        "symbol": symbol,
         "open": {
        "price": Close
        }
        }  
    
  CONTRASHORT = {
        "name": "CONTRA SHORT",
        "secret": "w48ulz23f6",
        "side": "sell",
        "symbol": symbol,
        "open": {
        "price": Close
        }
        }
  CONTRALONG = {
        "name": "CONTRA LONG",
        "secret": "xxuxkqf0gpj",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": Close
        }
        }
        
  DELFINLONG = {
        "name": "DELFIN LONG",
        "secret": "an0rvlxehbn",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": Close
        }
        }
  
  # TENDENCIA ALCISTA:
  if (diff > 1) and (Close > upperband[-2]) and (imbalance >= 0.6) and (adx[-2] >= 25):
    Tb.telegram_send_message(f"🎣 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\nIMB : {round(imbalance,2)} \n(🎣 Fishing Pisha")
    requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
  elif (diff > 1) and (Close) > upperband[-2] and (rsi >= 70) and (imbalance <= -0.6): 
    Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\nIMB : {round(imbalance,2)}")
    requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CONTRASHORT)   
        
        # TENDENCIA BAJISTA:
  if (diff > 1) and (Close < lowerband[-2]) and (imbalance <= -0.6) and (adx[-2] >= 25):
    Tb.telegram_send_message(f"🎣 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {Close}\nIMB : {round(imbalance,2)} \n🎣 Fishing Pisha")
    requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT)
  elif (diff > 1) and (Close < lowerband[-2]) and (rsi <= 30) and (imbalance >= 0.6): 
    Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\nIMB : {round(imbalance,2)}")
    requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=CONTRALONG)   
        
    #Cruce de EMAS + FIBO:
       
  if (ema_cross == 1) and (imbalance >  0.5):
    Tb.telegram_canal_prueba(f"🐬 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {Close}\nIMB : {round(imbalance,2)} \n🐬 Delfin")  
    requests.post('https://hook.finandy.com/9nQNB3NdMGaoK-xWqVUK', json=DELFINLONG) 
        
  if (ema_cross == -1) and (imbalance <  -0.5):
    Tb.telegram_canal_prueba(f"🐬 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {Close}\nIMB : {round(imbalance,2)} \n🐬 Delfin")
                  
while True:
  # Espera hasta que sea el comienzo de una nueva hora
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
    indicator(symbol)
    print(symbol)
