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
    
    rsi = ta.RSI(df["Close"], timeperiod=14)
    Close = float(df['Close'][-2])
    High = float(df['High'][-2])
    Low = float(df['Low'][-2])
    diff = abs((High / Low -1) * 100)
    #cci20 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)
    ema_200 = df['Close'].ewm(span=200, adjust=False).mean()
    #adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
    ad = ta.AD(df['High'], df['Low'], df['Close'], df['Volume'])
    df['Close'] = df['Close'].astype(float)
    delta = df['Close'].diff()
    fi = delta * ad
    #macd, signal, hist = ta.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
   
    
    
    upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
    #depth = 5
    #order_book = client.futures_order_book(symbol=symbol, limit=depth)

    #bid_sum = sum([float(bid[1]) for bid in order_book['bids']])
    #ask_sum = sum([float(ask[1]) for ask in order_book['asks']])
    #max_bid = float(order_book['bids'][0][0])
    #max_ask = float(order_book['asks'][0][0])
 
    #if bid_sum + ask_sum > 0:
     #imbalanceS = (ask_sum - bid_sum) / (bid_sum + ask_sum)
    #else:
     #imbalanceS = 0.0
    
    #depth = 5
    #order_book = client.futures_order_book(symbol=symbol, limit=depth)

    #bid_sum = sum([float(bid[1]) for bid in order_book['bids']])
    #ask_sum = sum([float(ask[1]) for ask in order_book['asks']])
    #max_bid = float(order_book['bids'][0][0])
    #max_ask = float(order_book['asks'][0][0])
    #mean_price = (max_ask + max_bid )/2
    #spread = max_ask - max_bid  # Calcula el spread
    #spread_por = ((max_ask - max_bid ) /mean_price)*100
 
    #if bid_sum + ask_sum > 0:
    # imbalance = (ask_sum - bid_sum) / (bid_sum + ask_sum)
    #else:
    # imbalance = 0.0
    
    #noro strategy
    ma = ta.SMA(df['Close'], timeperiod=3)
    long = ma + ((ma / 100) *(-1))
    short = ma + ((ma / 100) *(1))
       
    # Enviar la solicitud a la API pública de Binance
    response = requests.get(f'https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}')

# Obtener el volumen de negociación de las últimas 24 horas
    volume = float(response.json()['volume'])
    
    depth = 5
    order_book = client.futures_order_book(symbol=symbol, limit=depth)

    bid_sum = sum([float(bid[1]) for bid in order_book['bids']])
    ask_sum = sum([float(ask[1]) for ask in order_book['asks']])
    max_bid = float(order_book['bids'][0][0])
    max_ask = float(order_book['asks'][0][0])
 
    if bid_sum + ask_sum > 0:
     imbalance = (ask_sum - bid_sum) / (bid_sum + ask_sum)
    else:
     imbalance = 0.0              
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
  
  if (ema_200[-2] < Close) and (Close <= long[-2]) and (rsi[-2] <= 30):
      Tb.telegram_send_message(f"🎣 {symbol}\n🟢 LONG\n⏳ 15 min\n💵 Precio: {Close}\n🎣 Fishing Pisha")
      requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
         
  if (ema_200[-2] > Close) and (Close >= short[-2]) and (rsi[-2] >= 70):
      Tb.telegram_send_message(f"🎣 {symbol}\n🔴 SHORT\n⏳ 15 min\n💵 Precio: {Close}\n🎣 Fishing Pisha")
      requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT)   
          

while True:
  current_time = ti.time()
  seconds_to_wait = 900 - current_time % 900
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      
