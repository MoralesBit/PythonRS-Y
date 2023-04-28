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

url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
response = requests.get(url)
data = response.json()

symbols = [symbol['symbol'] for symbol in data['symbols'] if symbol['status'] == "TRADING"]
#symbols = ["BELUSDT", "BNXUSDT", "BTSUSDT", "CELOUSDT","FLMUSDT", "ICXUSDT", "INJUSDT", "IOSTUSDT", "OGNUSDT", "RAYUSDT"]

def indicator(symbol):
      
  kline = client.futures_historical_klines(symbol, "5m", "24 hours ago UTC+1",limit=500)
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
    Close = float(df['Close'][-2])
    df['ema_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    df['ema_13'] = df['Close'].ewm(span=13, adjust=False).mean()
    df['lrc'] = ta.LINEARREG(df['Close'], timeperiod=20)
        
    df['crossover'] = np.where(df['lrc'] > df['ema_13'],1,0)
    
    
    df['position'] = df['crossover'].diff()
    
        
    info = client.futures_historical_klines("BTCUSDT", "15m", "2 days ago UTC+1",limit=1000) 
    df_new = pd.DataFrame(info)
       
    if not df_new.empty:
        df_new.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close' 'IGNORE',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df_new['Date'] = pd.to_datetime(df_new['Date'], unit='ms')
    df_new = df_new.set_index('Date')
    cciB = ta.CCI(df_new['High'], df_new['Low'], df_new['Close'], timeperiod=28)
      
           
   # DATOS FNDY
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
      
  print(symbol)
     
# TENDENCIA :
  
  if (cciB[-2] > 0):
    if  df['position'][-2] == 1:    
      Tb.telegram_send_message(f"🎣 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {Close}\n🎣 Fishing Pisha")
      requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
      
  if (cciB[-2] < 0):       
   if df['position'][-2] == -1: 
      Tb.telegram_send_message(f"🎣 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {Close}\n🎣 Fishing Pisha")
      requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT)   
          

while True:
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      
