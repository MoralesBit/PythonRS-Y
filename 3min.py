
import requests
import pandas as pd
import numpy as np
import talib as ta
import Telegram_bot as Tb
import schedule as schedule
import time as ti
import json

api_key = 'TU_API_KEY'
api_secret = 'TU_API_SECRET'

futures_info_url = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
response = requests.get(futures_info_url).json()
symbols = [
    symbol['symbol'] for symbol in response['symbols']
    if symbol['status'] == "TRADING"
  ]

def indicator(symbol):
    
  url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=3m&startTime=12 hours ago UTC+1&limit=500'
  response = requests.get(url).json()
  df = pd.DataFrame(response, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
  df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
  df = df.set_index('Open time')
  if not df.empty:

    upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                                timeperiod=20,
                                                nbdevup=2,
                                                nbdevdn=2,
                                                matype=0)
    df['upperband'] = upperband
    df['middleband'] = middleband
    df['lowerband'] = lowerband
       
    rsi = ta.RSI(df["Close"], timeperiod=14)
    adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
    slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    
    Close = float(df['Close'][-2])
    Open = float(df['Open'][-2])
    High = float(df['High'][-2])
    Low = float(df['Low'][-2])
    diff = abs((High / Low -1) * 100)  

    
    PORSHORT = {
    "name": "CORTO 3POR",
    "secret": "ao2cgree8fp",
    "side": "sell",
    "symbol": symbol,
    "open": {
    "price": float(df['Close'][-2])
    }
    }
    PORLONG = {
    "name": "LARGO 3POR",
    "secret": "nwh2tbpay1r",
    "side": "buy",
    "symbol": symbol,
    "open": {
    "price": float(df['Close'][-2])
    }
    }
    
    url = f'https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=10'
    response = requests.get(url).json() 
    bids = response['bids']
    asks = response['asks']
    max_bid = max([float(bid[0]) for bid in bids])
    max_ask = max([float(ask[0]) for ask in asks])
    bid_sum = sum([float(bid[1]) for bid in bids])
    ask_sum = sum([float(ask[1]) for ask in asks])
    if bid_sum + ask_sum > 0:
        imbalance_btc = (ask_sum - bid_sum) / (bid_sum + ask_sum)
    else:
        imbalance_btc = 0.0
        
    depth = 30

    url = f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit={depth}'
    response = requests.get(url).json()
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
  
  #consigue max bid y ask
  url = f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit={depth}'
  response = requests.get(url).json() 
  if 'bids' in response and 'asks' in response:
        bids = response['bids']
        asks = response['asks']
        max_bid = max([float(bid[0]) for bid in bids])
        max_ask = max([float(ask[0]) for ask in asks])
  else:
    max_bid = 0
    max_ask = 0    
  
  print(imbalance)
  
  #Actual   
  if (diff > 1) and (Close > upperband[-2]) and (rsi[-2] > 70) and (slowk[-2] > 80) and (imbalance < -0.5):
    Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n IMB: {round(imbalance,2)} \n⛳️ Snipper : {max_ask} ") 
    requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT) 
  if (diff > 1) and (Close < lowerband[-2]) and (rsi[-2] < 30) and (slowk[-2] < 20) and (imbalance > 0.5):
    Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n IMB: {round(imbalance,2)} \n⛳️ Snipper : {max_bid} ")
    requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG)
  
  #PRUEBAS 3min
  if (rsi[-3] > 70) and (rsi[-2] <= 70) and (imbalance < -0.5) and (imbalance_btc < -0.5):
    Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n💵 Precio: {Close}\n IMB: {round(imbalance,2)}\n IMBTC: {round(imbalance_btc,2)} \n⛳️ Snipper : {max_ask} ") 
    requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT) 
  if (rsi[-3] < 30) and (rsi[-2] >= 30) and (imbalance > 0.5) and (imbalance_btc > 0.5):
    Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n💵 Precio: {Close}\n IMB: {round(imbalance,2)}\n IMBTC: {round(imbalance_btc,2)} \n⛳️ Snipper : {max_bid} ")
    requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG)
while True:
    # Espera hasta que sea el comienzo de una nueva hora
    current_time = ti.time()
    seconds_to_wait = 180 - current_time % 180
    ti.sleep(seconds_to_wait)   
  
    for symbol in symbols:
      indicator(symbol)
      print(symbol)
