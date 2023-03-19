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
  cci20 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)
    
  info = client.futures_historical_klines("BTCUSDT", "15m", "2 days ago UTC+1",limit=1000) 
  df_new = pd.DataFrame(info)
       
  if not df_new.empty:
        df_new.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close' 'IGNORE',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
  df_new['Date'] = pd.to_datetime(df_new['Date'], unit='ms')
  df_new = df_new.set_index('Date')
  
  cciB = ta.CCI(df_new['High'], df_new['Low'], df_new['Close'], timeperiod=28)
  cciB58 = ta.CCI(df_new['High'], df_new['Low'], df_new['Close'], timeperiod=58)
 
  print(symbol)
  print(df['position_macd'][-2])
    
       
  UNOSHORT = {
  "name": "SHORT-REV",
  "secret": "hgw3399vhh",
  "side": "sell",
  "symbol": symbol
  }
  UNOLONG = {
  "name": "LONG- REV",
  "secret": "xjth0i3qgb",
  "side": "buy",
  "symbol": symbol
  }
  
  if (cciB58[-3] < cciB58[-2]): 
    if (cci20[-3] < 0) and (cci20[-2] > 0):    
      requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=UNOLONG)
      Tb.telegram_send_message(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📈  Fast Trend")
  if (cciB58[-3] > cciB58[-2]): 
    if (cci20[-3] > 0) and (cci20[-2] < 0):   
      requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=UNOSHORT)  
      Tb.telegram_send_message(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📉  Fast Trend")
  
  
if __name__ == '__main__':
  monedas = client.futures_exchange_info()
  # 1. Obtener todas las monedas tradeables de futuros
  symbols = [
    symbol['symbol'] for symbol in monedas['symbols']
    if symbol['status'] == "TRADING"
  ]
#symbols = ["BLZUSDT", "ARUSDT", "INJUSDT", "STORJUSDT","HNTUSDT", "ARPAUSDT"]

def server_time():
          
  for symbol in symbols:
    indicator(symbol)
    ti.sleep(1)
            
schedule.every(3).minutes.at(":01").do(server_time)
  
while True:
    #server_time()
    schedule.run_pending()
    ti.sleep(1)
