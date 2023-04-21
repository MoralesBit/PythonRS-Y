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

# Calcular la señal de cruce
    ema_diff = ema_13 - ema_100
    crossing_index = np.where((ema_diff.shift(1) < 0) & (ema_diff > 0))[0]
    signal = pd.Series(0, index=df.index)
    signal.iloc[crossing_index] = 1
    signal.iloc[np.where((ema_diff.shift(1) > 0) & (ema_diff < 0))[0]] = -1

# ema 200
    
    
    upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
    depth = 5
    order_book = client.futures_order_book(symbol=symbol, limit=depth)

    bid_sum = sum([float(bid[1]) for bid in order_book['bids']])
    ask_sum = sum([float(ask[1]) for ask in order_book['asks']])
 
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
  print(signal[-2])
   
  
  
       # TENDENCIA ALCISTA:
  if (signal[-2] == 1) and (imbalance > 0.35):
          Tb.telegram_send_message(f"🎣 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {Close}\n⛳️ IMB : {round(imbalance,2)} \n🎣 Fishing Pisha")
          requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
  if (diff >= 1) and (Close >= upperband[-2]) and (rsi[-2] >= 70) and (imbalance <= -0.5): 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n⛳️ IMB : {round(imbalance,2)}")
          requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CONTRASHORT)   
        
        # TENDENCIA BAJISTA:
  if (signal[-2] == -1) and (imbalance < -0.35):
          Tb.telegram_send_message(f"🎣 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {Close}\n⛳️ IMB : {round(imbalance,2)}\n🎣 Fishing Pisha")
          requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT)
  if (diff >= 1) and (Close <= lowerband[-2]) and (rsi[-2] <= 30) and (imbalance >= 0.5): 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n⛳️ IMB : {round(imbalance,2)}")
          requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=CONTRALONG)  
  
  if (signal[-2] == 1) and (imbalance > 0) and (adx[-2] > 25):
        Tb.telegram_canal_prueba(f"EMA normal {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {Close}\nIMB : {round(imbalance,2)}")     
        requests.post('https://hook.finandy.com/9nQNB3NdMGaoK-xWqVUK', json=DELFINLONG) 
        
  if ((signal[-2] == -1)) and (imbalance < 0) and ((adx[-2] > 25)):
         Tb.telegram_canal_prueba(f"EMA normal {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {Close}\nIMB : {round(imbalance,2)}") 
                
while True:
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  #ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      
