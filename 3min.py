from binance.client import Client
import pandas as pd
import numpy as np
import talib as ta
import Telegram_bot as Tb
import  schedule as schedule
import time as ti
import requests
import json

Pkey = ''
Skey = ''

client = Client(api_key=Pkey, api_secret=Skey)

monedas = client.futures_exchange_info()
  # 1. Obtener todas las monedas tradeables de futuros
symbols = [
    symbol['symbol'] for symbol in monedas['symbols']
    if symbol['status'] == "TRADING"
  ]
#symbols = ["BLZUSDT", "ARUSDT", "INJUSDT", "STORJUSDT","HNTUSDT", "ARPAUSDT"]

def indicator(symbol):
  
  kline = client.futures_historical_klines(symbol, "3m", "2 days ago UTC+1",limit=1000)
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
  macd, signal, hist = ta.MACD(df['Close'], 
                                    fastperiod=12, 
                                    slowperiod=26, 
                                    signalperiod=9)
  df['macd'] = macd
  df['macd_signal'] = signal
  df['macd_hist'] = hist
  df['macd_crossover'] = np.where(df['macd'] > df['macd_signal'], 1, 0)
  df['position_macd'] = df['macd_crossover'].diff()
  
  rsi = ta.RSI(df["Close"], timeperiod=4)
  df['EMA100'] = df['Close'].ewm(100).mean()
  df['tendencia'] = np.where((float(df['Close'][-1])) > (df['EMA100'][-1]), 1,0)
  
  info = client.futures_historical_klines("BTCUSDT", "15m", "2 days ago UTC+1",limit=1000) 
  df_new = pd.DataFrame(info)
       
  if not df_new.empty:
    df_new.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close' 'IGNORE',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df_new['Date'] = pd.to_datetime(df_new['Date'], unit='ms')
    df_new = df_new.set_index('Date')
  
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
    
    bid_sum = sum([float(bid[1]) for bid in bids])
    ask_sum = sum([float(ask[1]) for ask in asks])
   
   
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
  if (diff > 1) and (Close > upperband[-2]) and (rsi[-2] > 70)and (imbalance < -0.7) and (adx[-2] >= 40):
    Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n IMB: {round(imbalance,2)}") 
    requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT) 
  if (diff > 1) and (Close < lowerband[-2]) and (rsi[-2] < 30) and (imbalance > 0.7) and (adx[-2] <= 20):
    Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n IMB: {round(imbalance,2)}")
    requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG)    
       
while True:
      # Espera hasta que sea el comienzo de una nueva hora
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
    indicator(symbol)
    print(symbol)
