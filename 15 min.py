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
#symbols = ["BLZUSDT", "ARUSDT", "INJUSDT", "STORJUSDT","HNTUSDT", "ARPAUSDT"]

def indicator(symbol):
  
  kline = client.futures_historical_klines(symbol, "15m", "24 hours ago UTC+1",limit=500)
  df = pd.DataFrame(kline)
  
  if not df.empty:
      df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
            'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
      df['Date'] = pd.to_datetime(df['Date'], unit='ms')
      df = df.set_index('Date')
      
      Close = float(df['Close'][-2])
      
      klines = client.futures_klines(symbol=symbol, interval='15m')
      close_prices = np.asarray([float(entry[4]) for entry in klines])
      # Calcular el CCI con la fórmula directa
      typical_prices = (close_prices + close_prices + close_prices) / 3
      ma = ta.SMA(typical_prices, timeperiod=20)
      deviation = ta.STDDEV(typical_prices, timeperiod=20, nbdev=1)
      cci_new = (typical_prices - ma) / (0.015 * deviation)
      cci_20 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)
      
    
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
  if (cci_20[-2] >= cci_new[-2]):
      Tb.telegram_canal_prueba(f"🎣 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {Close}\n🎣 Fishing Pisha")
      requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
      
  if (cci_20[-2] <= cci_new[-2]):
      Tb.telegram_canal_prueba(f"🎣 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {Close}\n🎣 Fishing Pisha")
      requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT)   
          

while True:
  current_time = ti.time()
  seconds_to_wait = 900 - current_time % 900
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      
