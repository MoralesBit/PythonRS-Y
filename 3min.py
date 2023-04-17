from binance.client import Client
import pandas as pd
import numpy as np
import talib as ta
import Telegram_bot as Tb
import  schedule as schedule
import time as ti
import requests
import json


api_key = 'TU_API_KEY'
api_secret = 'TU_API_SECRET'

client = Client(api_key, api_secret)

futures_info = client.futures_exchange_info()
symbols = [
    symbol['symbol'] for symbol in futures_info['symbols']
    if symbol['status'] == "TRADING"
  ]

def indicator(symbol):
    
  kline = client.futures_historical_klines(symbol, "3m", "12 hours ago UTC+1",limit=500)
  df = pd.read_json(json.dumps(kline))
    
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close' 'IGNORE',
    'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
      
    
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
    depth = 5

    response = requests.get(f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit={depth}').json()
    bid_max= max([float(bid[1]) for bid in response['bids']])
    ask_max = max([float(ask[1]) for ask in response['asks']])
    
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
    
  #Actual   
  if (diff > 1) and (Close > upperband[-2]) and (rsi[-2] > 70) and (adx[-2] >= 40) and (slowk[-2] > 95):
    Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n IMB: {round(imbalance,2)} \n⛳️ Snipper : {ask_max} ") 
    requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT) 
  if (diff > 1) and (Close < lowerband[-2]) and (rsi[-2] < 30) and (adx[-2] <= 20) and (slowk[-2] < 5):
    Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n IMB: {round(imbalance,2)} \n⛳️ Snipper : {bid_max} ")
    requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG)
    
      
while True:
    # Espera hasta que sea el comienzo de una nueva hora
    current_time = ti.time()
    seconds_to_wait = 180 - current_time % 180
    ti.sleep(seconds_to_wait)   
  
    for symbol in symbols:
      indicator(symbol)
      print(symbol)
