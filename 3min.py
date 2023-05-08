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
  
  kline = client.futures_historical_klines(symbol, "3m", "24 hours ago UTC+1",limit=500)
  df = pd.DataFrame(kline)
  
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
    
    #Calculo RSI:
    rsi = ta.RSI(df["Close"], timeperiod=14)
        
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
    df['OHLC4'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    
    df['diff'] = abs((df['High'] / df['Low'] -1) * 100)
    
    df['enter_high'] = (df['Close'] +  df['High'] )/2
    df['enter_low'] = (df['Close']  + df['Low'])/2
     
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
          
    
  PICKERSHORT= {
  "name": "PICKER SHORT",
  "secret": "hgw3399vhh",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": df['enter_high'][-2] 
  }
}
  PICKERLONG = {
  "name": "PICKER LONG",
  "secret": "xjth0i3qgb",
  "side": "buy",
  "symbol": symbol,
  "open": {
    "price": df['enter_low'][-2]
  }
}
    
  CARLOSSHORT = {
  "name": "Hook 200276",
  "secret": "gwbzsussxu5",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price":  df['enter_high'][-2] 
  }
}
   
  print(df['diff'][-2])
  if (df['Close'][-2] < lowerband[-2]) and (df['diff'][-2] > 3) and (imbalance > 0.55):
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(df['diff'][-2],2)} \n💵 Precio: {df['Close'][-2]}\n📍 Picker: {round(df['enter_low'][-2],6)}") 
      requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=PICKERLONG)
      
  if (df['Close'][-2] > upperband[-2]) and (df['diff'][-2] > 3) and (imbalance < -0.55):
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(df['diff'][-2],2)} \n💵 Precio: {df['Close'][-2]}\n📍 Picker: {round(df['enter_high'][-2],6)}")
      requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=PICKERSHORT)
      requests.post('https://hook.finandy.com/DRt05cAn8UjMWv5bqVUK', json=CARLOSSHORT) 

               
while True:
  current_time = ti.time()
  seconds_to_wait = 180 - current_time % 180
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      print(symbol)
