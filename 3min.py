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
    
    macd, signal, hist = ta.MACD(df['Close'], 
                                      fastperiod=12, 
                                      slowperiod=26, 
                                      signalperiod=9)
    df['macd'] = macd
    df['macd_signal'] = signal
    df['macd_hist'] = hist
    df['macd_crossover'] = np.where(df['macd'] > df['macd_signal'], 1, 0)
    df['position_macd'] = df['macd_crossover'].diff()
    
    rsi = ta.RSI(df["Close"], timeperiod=14)
    adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
    slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    df['Will'] = ta.WILLR(df['High'], df['Low'], df['Close'], timeperiod=14)
    df['BBW'] = (df['upperband'] - df['lowerband']) / df['middleband']  
    chain = ta.ADOSC(df['High'], df['Low'], df['Close'], df['Volume'], fastperiod=3, slowperiod=10)
  
    df['EMA200'] = df['Close'].ewm(200).mean()
    df['EMA100'] = df['Close'].ewm(100).mean()
    
    df['tendencia'] = np.where((float(df['Close'][-2])) > (df['EMA100'][-2]),1,0)
    df['tendenciaemas'] = np.where(df['EMA100'][-2] > (df['EMA200'][-2]),1,0)
    
    df['max_price'] = (df['Close']).max()
    df['min_price'] = (df['Close']).min()
      
      
    df['diference'] = df['max_price'] - df['min_price']
      
    df['first_level'] = df['max_price'] -  df['diference']*0.236
    df['secound_level'] = df['max_price'] -  df['diference']* 0.382
    df['third_level'] = df['max_price'] -  df['diference']*0.5
    df['fourth_level'] = df['max_price'] -  df['diference']*0.618
    
    df['first_cross'] = np.where((float(df['Close'][-2])) > (df['first_level']),1,0)
    df['secound_cross'] = np.where((float(df['Close'][-2])) > (df['secound_level']),1,0)
    df['third_cross'] = np.where((float(df['Close'][-2])) > (df['third_level']),1,0)
    df['fourth_cross'] = np.where((float(df['Close'][-2])) > (df['fourth_level']),1,0)
    
    Close = float(df['Close'][-2])
    Open = float(df['Open'][-2])
    High = float(df['High'][-2])
    Low = float(df['Low'][-2])
    diff = abs((High / Low -1) * 100)  

    depth = client.futures_order_book(symbol=symbol, limit=50)
    bids = depth['bids']
    asks = depth['asks']
    max_bid = max([float(bid[0]) for bid in bids[-30:]])
    max_ask = max([float(ask[0]) for ask in asks[-30:]])
    
      
    PORSHORT = {
    "name": "CORTO 3POR",
    "secret": "ao2cgree8fp",
    "side": "sell",
    "symbol": symbol,
    "open": {
    "price": max_ask
    }
    }
    PORLONG = {
    "name": "LARGO 3POR",
    "secret": "nwh2tbpay1r",
    "side": "buy",
    "symbol": symbol,
    "open": {
    "price": max_bid
    }
    }
     
   
  if (diff > 1) and (rsi[-2] > 70) and (Close > df['upperband'][-2]):
    Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close} \n⛳️ Snipper : {max_ask} ") 
    requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT) 
  if (diff > 1) and (rsi[-2] < 70) and (Close < df['lowerband'][-2]):
    Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close} \n⛳️ Snipper : {max_bid} ")
    requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG)
    
while True:
    # Espera hasta que sea el comienzo de una nueva hora
    current_time = ti.time()
    seconds_to_wait = 180 - current_time % 180
    ti.sleep(seconds_to_wait)   
  
    for symbol in symbols:
      indicator(symbol)
      print(symbol)
