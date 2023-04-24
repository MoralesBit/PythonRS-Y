from binance.client import Client
import pandas as pd
import talib as ta
import Telegram_bot as Tb
import  schedule as schedule
import time as ti
import requests
import numpy as np

Pkey = ''
Skey = ''

client = Client(api_key=Pkey, api_secret=Skey)

futures_info = client.futures_exchange_info()

symbols = [
    symbol['symbol'] for symbol in futures_info['symbols']
    if symbol['status'] == "TRADING"
  ]

def indicator(symbol):
  
  kline = client.futures_historical_klines(symbol, "5m", "20 hours ago UTC+1",limit=500)
  df = pd.DataFrame(kline)
  
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
    
    rsi = ta.RSI(df["Close"], timeperiod=14)
    adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
    
    Close = float(df['Close'][-2])
    High = float(df['High'][-2])
    Low = float(df['Low'][-2])
    diff = abs((High / Low -1) * 100)
    
    # Calcular las EMAs de 13 días y 100 días
    ema_13 = df['Close'].ewm(span=13, adjust=False).mean()
    ema_100 = df['Close'].ewm(span=100, adjust=False).mean()
    ema_200 = df['Close'].ewm(span=200, adjust=False).mean()

    
# Detectar el cruce de las EMAs y enviar una señal
    signal = pd.Series(0, index=df.index)
    for i in range(1, len(df)):
            if (ema_13.iloc[i] > ema_100.iloc[i]) and (ema_13.iloc[i-1] <= ema_100.iloc[i-1]):
                  signal.iloc[i] = 1
            elif (ema_13.iloc[i] < ema_100.iloc[i]) and (ema_13.iloc[i-1] >= ema_100.iloc[i-1]):
                  signal.iloc[i] = -1

# Calcular el punto exacto del cruce
    crossing_points = pd.Series(index=signal.index, dtype='float64')
    for i in range(1, len(signal)):
     if (signal.iloc[i] == 1) or (signal.iloc[i] == -1):
        x0, x1 = ema_13.index[i-1], ema_13.index[i]
        y0, y1 = ema_13.iloc[i-1], ema_13.iloc[i]
        crossing_points.iloc[i] = x0 + (x1 - x0) * (y0 / (y0 - y1))
    
    upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
    depth = 5
    order_book = client.futures_order_book(symbol=symbol, limit=depth)

    bid_sum = sum([float(bid[1]) for bid in order_book['bids']])
    ask_sum = sum([float(ask[1]) for ask in order_book['asks']])
    max_bid = float(order_book['bids'][0][0])
    max_ask = float(order_book['asks'][0][0])
 
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
        "price": ema_13[-2]
        }
        }
        
  FISHINGLONG = {
        "name": "FISHING LONG",
        "secret": "0kivpja7tz89",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": ema_13[-2]
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
     
  print(symbol)
    
  
# TENDENCIA :
  if (signal[-2] == 1) and (bid_sum[-2] > ask_sum[-2]):
      Tb.telegram_send_message(f"🎣 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio in: {round(ema_13[-2],2)}\n🎣 Fishing Pisha")
      requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
      
  if ((signal[-2] == -1)) and (ask_sum > bid_sum):
      Tb.telegram_send_message(f"🎣 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio in: {round(ema_13[-2],2)}\n🎣 Fishing Pisha")
      requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT)   
          
#CONTRA TENDENCIA        
  if (diff >= 1) and (Close >= upperband[-2]) and (rsi[-2] >= 80) and (ask_sum > bid_sum): 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n📉 RSI: {rsi[-2]}")
          requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CONTRASHORT)   
  
  if (diff >= 1) and (Close <= lowerband[-2]) and (rsi[-2] <= 20) and (ask_sum < bid_sum): 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n📈 RSI: {rsi[-2]}")
          requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=CONTRALONG)  
  
  #if (signal[-2] == 1) and (imbalance > 0) and (adx[-2] > 25):
        #Tb.telegram_canal_prueba(f"EMA normal {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {Close}\nIMB : {round(imbalance,2)}")     
        #requests.post('https://hook.finandy.com/9nQNB3NdMGaoK-xWqVUK', json=DELFINLONG) 
        
  #if ((signal[-2] == -1)) and (imbalance < 0) and ((adx[-2] > 25)):
         #Tb.telegram_canal_prueba(f"EMA normal {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {Close}\nIMB : {round(imbalance,2)}") 
                
while True:
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      
