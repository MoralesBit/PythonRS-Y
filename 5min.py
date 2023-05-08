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
  
  kline = client.futures_historical_klines(symbol, "5m", "24 hours ago UTC+1",limit=1000)
  df = pd.DataFrame(kline)
  
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
    
          
    # Calculo Bollinger:
    upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
       
    #noro strategy
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
       
    df['diff'] = abs((df['High'] / df['Low'] -1) * 100)
     
    
    df['BB'] = (df['Close'] - lowerband) / ( upperband - lowerband)
        
          
   
    PICKERSHORT= {
  "name": "PICKER SHORT",
  "secret": "hgw3399vhh",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": df['Open'][-1]
  }
}
    PICKERLONG = {
  "name": "PICKER LONG",
  "secret": "xjth0i3qgb",
  "side": "buy",
  "symbol": symbol,
  "open": {
    "price": df['Open'][-1]
  }
}
    
# KC strategy:
  if  (df['Close'][-3] < lowerband[-3]) and (df['diff'][-3] > 2) and (df['BB'][-1] > 0): 
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Cambio: % {round(df['diff'][-3],2)} \n💵 Precio: {df['Close'][-2]}\n📍 Picker: {round(df['Open'][-1],6)}") 
      requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=PICKERLONG)
      
  if (df['Close'][-3] > upperband[-3]) and (df['diff'][-3] > 2) and (df['BB'][-1] < 1): 
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Cambio: % {round(df['diff'][-3],2)} \n💵 Precio: {df['Close'][-2]}\n📍 Picker: {round(df['Open'][-1],6)}")
      requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=PICKERSHORT)
   
      
               
while True:
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      print(symbol)
