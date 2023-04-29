from binance.client import Client
import pandas as pd
import talib as ta
import Telegram_bot as Tb
import time as ti
import requests
import numpy as np

Pkey = ''
Skey = ''

client = Client(api_key=Pkey, api_secret=Skey)

futures_info = client.futures_exchange_info()

#symbols = [
#    symbol['symbol'] for symbol in futures_info['symbols']
#    if symbol['status'] == "TRADING"
#  ]
symbols = ["STMXUSDT", "ALPHAUSDT", "ICPUSDT", "DYDXUSDT","LUNA2USDT"]

def indicator(symbol):
      
  kline = client.futures_historical_klines(symbol, "5m", "24 hours ago UTC+1",limit=500)
  df = pd.DataFrame(kline)
  
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
#    upperband, middleband, lowerband = ta.BBANDS(df['Close'],
#                                               timeperiod=20,
#                                               nbdevup=2,
#                                               nbdevdn=2,
#                                               matype=0)
    Close = float(df['Close'][-2])
    
# Calcular la EMA de 200 y 13 períodos y la LRC de 20 períodos
    df['ema_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    df['ema_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=5, slowk_matype=0, slowd_period=3, slowd_matype=0)

           
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
      
  
 
       
# TENDENCIA :
  
  
  if  (slowk[-3] < slowd[-3]) and (slowk[-2]> slowd[-2]) and (Close > df['ema_50'][-2] > df['ema_200'][-2]):    
      Tb.telegram_canal_prueba(f"🎣 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {Close}\n🎣 Fishing Pisha")
      requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
      
         
  if (slowk[-3] > slowd[-3]) and (slowk[-2] < slowd[-2]) and (Close < df['ema_50'][-2] < df['ema_200'][-2]):  
      Tb.telegram_canal_prueba(f"🎣 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {Close}\n🎣 Fishing Pisha")
      requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT)   
          

while True:
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      print(symbol)
      
