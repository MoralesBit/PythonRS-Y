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
      ma = ta.SMA(typical_prices, timeperiod=28)
      deviation = ta.STDDEV(typical_prices, timeperiod=28, nbdev=1)
      cci_new = (typical_prices - ma) / (0.015 * deviation)
      cci_20 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=28)
      ema_200 = df['Close'].ewm(span=200, adjust=False).mean()
      adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
      
# Enviar la solicitud a la API pública de Binance
      response = requests.get(f'https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}')

# Obtener el volumen de negociación de las últimas 24 horas
      volume = float(response.json()['volume'])
      depth = 5
      order_book = client.futures_order_book(symbol='BTCUSDT', limit=depth)

      bid_sum = sum([float(bid[1]) for bid in order_book['bids']])
      ask_sum = sum([float(ask[1]) for ask in order_book['asks']])
      max_bid = float(order_book['bids'][0][0])
      max_ask = float(order_book['asks'][0][0])
 
      if bid_sum + ask_sum > 0:
            imbalance = (ask_sum - bid_sum) / (bid_sum + ask_sum)
      else:
            imbalance = 0.0
      klines = client.futures_historical_klines("BTCUSDT", "15m", "24 hours ago UTC+1",limit=500)
      df_new = pd.DataFrame(klines)
  
      if not df_new.empty:
                  df_new.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
                  'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
                  df_new['Date'] = pd.to_datetime(df_new['Date'], unit='ms')
                  df_new = df_new.set_index('Date')
                  ema_200_new = df_new['Close'].ewm(span=200, adjust=False).mean()
                  Close_new = float(df_new['Close'][-2])
                  
                  
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
  if (Close_new > ema_200_new[-2]):
      if (ema_200[-2] < Close) and (cci_20[-2] >= cci_new[-2]) and (imbalance > 0.6):
            Tb.telegram_send_message(f"🎣 {symbol}\n🟢 LONG\n⏳ 15 min\n💵 Precio: {Close}\n🎣 Fishing Pisha")
            requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
  if (Close_new < ema_200_new[-2]):    
      if (ema_200[-2] > Close) and (cci_20[-2] <= cci_new[-2]) and (imbalance < -0.6):
            Tb.telegram_send_message(f"🎣 {symbol}\n🔴 SHORT\n⏳ 15 min\n💵 Precio: {Close}\n🎣 Fishing Pisha")
            requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT)   
          

while True:
  current_time = ti.time()
  seconds_to_wait = 900 - current_time % 900
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      
