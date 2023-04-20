
import requests
import pandas as pd
import numpy as np
import talib as ta
import Telegram_bot as Tb
import schedule as schedule
import time as ti
import json
from binance.client import Client


Pkey = ''
Skey = ''

client = Client(api_key=Pkey, api_secret=Skey)

monedas = client.futures_exchange_info()
  # 1. Obtener todas las monedas tradeables de futuros
symbols = [
    symbol['symbol'] for symbol in monedas['symbols']
    if symbol['status'] == "TRADING"
  ]
#symbols = ["BLZUSDT", "ARUSDT", "INJUSDT", "STORJUSDT","HNTUSDT", "ARPAUSDT"]

def indicator(symbol):
      
  kline = client.futures_historical_klines(symbol, "15m", "2 days ago UTC+1",limit=1000)
  df = pd.DataFrame(kline)
  
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
      
    
    upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                                timeperiod=20,
                                                nbdevup=2,
                                                nbdevdn=2,
                                                matype=0)
    df['upperband'] = upperband
    df['middleband'] = middleband
    df['lowerband'] = lowerband
          
    rsi = ta.RSI(df["Close"], timeperiod=14)
    adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
                         
    df['EMA13'] = df['Close'].ewm(13).mean()
    df['EMA200'] = df['Close'].ewm(200).mean()
    df['EMA100'] = df['Close'].ewm(100).mean()
    High = float(df['High'][-2])
    Low = float(df['Low'][-2])
    diff = abs((High / Low -1) * 100) 
    
    # DATOS FNDY
    FISHINGSHORT = {
        "name": "FISHING SHORT",
        "secret": "azsdb9x719",
        "side": "sell",
        "symbol": symbol,
        "open": {
        "price": float(df['Close'][-2])
        }
        }
        
    FISHINGLONG = {
        "name": "FISHING LONG",
        "secret": "0kivpja7tz89",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": float(df['Close'][-2])
        }
        }
    
    BOUNCYSHORT = {
        "name": "BOUNCY SHORT",
        "secret": "hgw3399vhh",
        "side": "sell",
        "symbol": symbol,
         "open": {
        "price": float(df['Close'][-2])
        }
        }
        
    BOUNCYLONG = {
        "name": "BOUNCY LONG",
        "secret": "xjth0i3qgb",
        "side": "buy",
        "symbol": symbol,
         "open": {
        "price": float(df['Close'][-2])
        }
        }  
    
    CONTRASHORT = {
        "name": "CONTRA SHORT",
        "secret": "w48ulz23f6",
        "side": "sell",
        "symbol": symbol,
        "open": {
        "price": float(df['Close'][-2])
        }
        }
    CONTRALONG = {
        "name": "CONTRA LONG",
        "secret": "xxuxkqf0gpj",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": float(df['Close'][-2])
        }
        }
        
    DELFINLONG = {
        "name": "DELFIN LONG",
        "secret": "an0rvlxehbn",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": float(df['Close'][-2])
        }
        }
            
    depth = 5

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
        
                                                       
        # TENDENCIA ALCISTA:
    if (diff > 1) and (float(df['Close'][-2]) > upperband[-2]) and (imbalance >= 0.5) and (adx[-2] <= 25):
          Tb.telegram_send_message(f"🎣 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\n⛳️ IMB : {round(imbalance,2)} \n(🎣 Fishing Pisha")
          requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
    elif (diff > 1) and (float(df['Close'][-2]) > upperband[-2]) and (rsi[-2] >= 75) and (imbalance <= -0.6): 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Cambio: % {round(df['diff'][-3],2)} \n💵 Precio: {float(df['Close'][-2])}\n⛳️ IMB : {round(imbalance,2)}")
          requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CONTRASHORT)   
        
        # TENDENCIA BAJISTA:
    if (diff > 1) and (float(df['Close'][-2]) < lowerband[-2]) and (imbalance <= -0.5) and (adx[-2] >= 45):
          Tb.telegram_send_message(f"🎣 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\n⛳️ IMB : {round(imbalance,2)} \n🎣 Fishing Pisha")
          requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT)
    elif (diff > 1) and (float(df['Close'][-2]) < lowerband[-2]) and (rsi[-2] <= 25) and (imbalance >= 0.6): 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Cambio: % {round(df['diff'][-3],2)} \n💵 Precio: {float(df['Close'][-2])}\n⛳️ IMB : {round(imbalance,2)}")
          requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=CONTRALONG)   
        
         #Cruce de EMAS + FIBO:
       
    if (imbalance >  0.9):
      Tb.telegram_canal_prueba(f"🐬 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\nIMB : {round(imbalance,2)} \n🐬 Delfin")  
      #requests.post('https://hook.finandy.com/9nQNB3NdMGaoK-xWqVUK', json=DELFINLONG) 
        
    if (imbalance <  -0.9):
      Tb.telegram_canal_prueba(f"🐬 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\nIMB : {round(imbalance,2)} \n🐬 Delfin")
                  
while True:
  # Espera hasta que sea el comienzo de una nueva hora
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
    indicator(symbol)
    print(symbol)
