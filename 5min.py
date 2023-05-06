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
  
  kline = client.futures_historical_klines(symbol, "5m", "2 days ago UTC+1",limit=1000)
  df = pd.DataFrame(kline)
  
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
    
    roc = ta.ROC(df['Close'], timeperiod=10)
    
    adx= ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
    
    df['ema_660'] = df['Close'].ewm(span=660, adjust=False).mean()
    
    #Calculo RSI:
    rsi = ta.RSI(df["Close"], timeperiod=14)
    
    #BB
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
    enter_high = Close + Close*abs(average_candle_size/100)
    enter_low = Close - Close*abs(average_candle_size/100)
                 
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
    "price": Close
  }
}


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
   
   
      
# strategy Back:
  if (diff >= 3) and (df['BB'][-1] > 0):
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Avg: % {round(average_candle_size,2)} \n💵 Precio: {Close}\n📍 Picker: {round(enter_low,6)}") 
      requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=PICKERLONG)
      
  if (diff >= 3)  and (df['BB'][-1] < 1):
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Avg: % {round(average_candle_size,2)} \n💵 Precio: {Close}\n📍 Picker: {round(enter_high,6)}")
      requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=PICKERSHORT)
      requests.post('https://hook.finandy.com/DRt05cAn8UjMWv5bqVUK', json=CARLOSSHORT) 

# strategy Trend:
  if (Close < df['ema_660'][-2]) and (adx[-2] > 20):
    if (df['BB'][-2] >= 0.9):      
      Tb.telegram_send_message(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n💵 Precio: {Close}\n🎣 Fishing Pisha")
      requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT) 
  
  if (Close > df['ema_660'][-2]) and (adx[-2] > 20):
    if (df['BB'][-2] < 0.1):  
      Tb.telegram_send_message(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n💵 Precio: {Close}\n🎣 Fishing Pisha") 
      requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG)


while True:
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      print(symbol)
