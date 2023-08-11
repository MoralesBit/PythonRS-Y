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
#symbols = ["BTCUSDT", "XRPUSDT", "BNBUSDT", "ADAUSDT","DOGEUSDT", "SOLUSDT", "TRXUSDT", "LTCUSDT" , "MATICUSDT", "BCHUSDT", "AVAXUSDT","1000SHIBUSDT","LINKUSDT","XLMUSDT","UNIUSDT","ATOMUSDT","XMRUSDT","FILUSDT"]  

def indicator(symbol):
  
  url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=5m&startTime=2 days ago UTC+1&limit=500'
  response = requests.get(url).json()
  df = pd.DataFrame(response, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
  df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
  df = df.set_index('Open time')
  if not df.empty:
      
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)

    df['rsi'] = ta.RSI(df['Close'], timeperiod=14)
    
    df['cmf'] = (((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (df["High"] - df["Low"]))
    
    df['adx'] = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
       
    if df['cmf'][-2] < 0 and df['adx'][-2] >= 45 and df['rsi'][-2] >= 75:
                
                    Tb.telegram_canal_3por(f"🔴 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}\n📍 Picker ▫️ 5 min")
                    PICKERSHORT = {
                    "name": "PICKER SHORT",
                    "secret": "ao2cgree8fp",
                    "side": "sell",
                    "symbol": symbol,
                    "open": {
                    "price": float(df['Close'][-1]) 
                    }
                    }
                    requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PICKERSHORT) 
    
    elif df['cmf'][-2] > 0 and df['adx'][-2] <= 15  and df['rsi'][-2] <= 30:
                
                    Tb.telegram_canal_3por(f"🟢 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}\n📍 Picker  ▫️ 5 min")
                    PICKERLONG = {
                    "name": "PICKER LONG",
                    "secret": "nwh2tbpay1r",
                    "side": "buy",
                    "symbol": symbol,
                    "open": {
                    "price": float(df['Close'][-1])
                    }
                    }
                    requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PICKERLONG)  
                                                                 
    else:
                print("NO")

               
while True:
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      print(symbol)
      
