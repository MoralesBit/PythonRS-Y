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
  
  kline = client.futures_historical_klines(symbol, "5m", "24 hours ago UTC+1",limit=500)
  df = pd.DataFrame(kline)
  
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
    
    
    # Calculo Bollinger:
    df['upperband'], df['middleband'], df['lowerband'] = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
       
  
    df[['open', 'high', 'low', 'close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
    
    df['BB'] = (df['close'] - df['lowerband']) / (df['upperband'] - df['lowerband'])
        
    df['diff'] = abs((df['high'] / df['low'] -1) * 100)      
   
    PICKERSHORT= {
  "name": "PICKER SHORT",
  "secret": "hgw3399vhh",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": df['Open'][-2]
  }
}
    PICKERLONG = {
  "name": "PICKER LONG",
  "secret": "xjth0i3qgb",
  "side": "buy",
  "symbol": symbol,
  "open": {
    "price": df['Open'][-2]
  }
}
    
# KC strategy:
  if  (df['close'][-3] < df['lowerband'][-3]) and (df['diff'][-3] >= 2) and (df['high'][-2] > df['lowerband'][-2]): 
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Cambio: % {round(df['diff'][-3],2)} \n💵 Precio: {df['close'][-2]}\n📍 Picker: {round(df['open'][-2],6)}") 
      requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=PICKERLONG)
      
  if (df['close'][-3] > df['upperband'][-3]) and (df['diff'][-3] >= 2) and (df['low'][-2] < df['upperband'][-2]):
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Cambio: % {round(df['diff'][-3],2)} \n💵 Precio: {df['close'][-2]}\n📍 Picker: {round(df['0pen'][-2],6)}")
      requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=PICKERSHORT)
   
      
               
while True:
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      print(symbol)
