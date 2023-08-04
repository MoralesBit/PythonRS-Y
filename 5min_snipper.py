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
  
  kline = client.futures_historical_klines(symbol, "5m", "24 hours ago UTC+1",limit=1000)
  df = pd.DataFrame(kline)
  
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
      
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
    df['diff'] = abs((df['High'] / df['Low'] -1) * 100)
    
    #Imbalance
    depth = 3

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
    
    if imbalance < -0.8: 
      if df['diff'][-2] >= 1:
                    Tb.telegram_canal_prueba(f"🔴 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}\n📍 Picker ▫️ 5 min")
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
    elif imbalance > 0.8:                 
      if df['diff'][-2] >= 1:
                    Tb.telegram_canal_prueba(f"🟢 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}\n📍 Picker  ▫️ 5 min")
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
