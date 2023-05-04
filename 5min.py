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
    
    df['upperband'], df['middleband'], df['lowerband'] = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
     
    # Calculo de DIFF:
    Close = float(df['Close'][-2])
    High = float(df['High'][-2])
    Low = float(df['Low'][-2])
    Open = float(df['Open'][-2])
    diff = abs((High / Low -1) * 100)


    df['STD_5'] = ta.STDDEV(df['Close'], timeperiod=5, nbdev=1)
    df['STD_5_promedio'] = df['STD_5'].mean()

        
    #noro strategy
    df['Open'] = df['Open'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Close'] = df['Close'].astype(float)
    df['OHLC4'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    
    df['BB'] = (df['Close'] - df['lowerband']) / ( df['upperband'] - df['lowerband'])
       
    candle_size = abs(df['Close'] - df['Open']) / df['Open'] * 100
    average_candle_size = np.mean(candle_size[-12:])
    
    # Entradas en cola:
    enter_high = (Close + High)/2
    enter_low = (Close + Low)/2
                 
    PICKERSHORT= {
  "name": "PICKER SHORT",
  "secret": "hgw3399vhh",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": enter_high
  }
}
    PICKERLONG = {
  "name": "PICKER LONG",
  "secret": "xjth0i3qgb",
  "side": "buy",
  "symbol": symbol,
  "open": {
    "price": enter_low
  }
}
    
    CARLOSSHORT = {
  "name": "Hook 200276",
  "secret": "gwbzsussxu5",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": enter_high
  }
}

   
   
# strategy:
  if (diff > 0.5) and (df['BB'][-2] < 0) and (df['BB'][-1] > 0):
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Cambio: % {round(average_candle_size,2)} \n💵 Precio: {Close}\n📍 Picker: {round(enter_low,6)}") 
      requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=PICKERLONG)
      
  if (diff > 0.5)  and (df['BB'][-2] > 1) and (df['BB'][-1] < 1):
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Cambio: % {round(average_candle_size,2)} \n💵 Precio: {Close}\n📍 Picker: {round(enter_high,6)}")
      requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=PICKERSHORT)
      #requests.post('https://hook.finandy.com/DRt05cAn8UjMWv5bqVUK', json=CARLOSSHORT) 


while True:
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      print(symbol)
