from binance.client import Client
import pandas as pd
import numpy as np
import talib as ta
import Telegram_bot as Tb
import  schedule as schedule
import time as ti
import requests

Pkey = ''
Skey = ''

client = Client(api_key=Pkey, api_secret=Skey)

intervals = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57]
connection = ""
period = 14


def indicator(symbol):
  rsi_stat = ""
   
  kline = client.futures_historical_klines(symbol, "3m", "24 hours ago UTC+1",limit=1000)
  df = pd.DataFrame(kline)
  
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close' 'IGNORE',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
    
  df['EMA13'] = df['Close'].ewm(13).mean()
  df['EMA50'] = df['Close'].ewm(50).mean()
  df['EMA100'] = df['Close'].ewm(100).mean()
  df['EMA200'] = df['Close'].ewm(200).mean()
  
  df['signal'] = 0
    
  df['signal'] = np.where(df['EMA13'] > df['EMA100'], 1,0)
  
  df['Positions'] = df['signal'].diff()  
  
  upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
  macd, signal, hist = ta.MACD(df['Close'], 
                                    fastperiod=12, 
                                    slowperiod=26, 
                                    signalperiod=9)
   
  cci = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=58)
  
  adxr = ta.ADXR(df['High'], df['Low'], df['Close'], timeperiod=14)
  
  roc = ta.ROC(df['Close'], timeperiod=10)
  
  rsi = ta.RSI(df["Close"], timeperiod=period)
  
  Close = float(df['Close'][-1])
  
  adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
 
  last_rsi = rsi 
  
  info = client.futures_historical_klines("BTCUSDT", "3m", "24 hours ago UTC+1",limit=1000) 
  df_new = pd.DataFrame(info)
       
  if not df_new.empty:
        df_new.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close' 'IGNORE',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
  df_new['Date'] = pd.to_datetime(df_new['Date'], unit='ms')
  df_new = df_new.set_index('Date')
  cciB = ta.CCI(df_new['High'], df_new['Low'], df_new['Close'], timeperiod=58)
  macdB, signalB, histB = ta.MACD(df_new['Close'], 
                                    fastperiod=12, 
                                    slowperiod=26, 
                                    signalperiod=9)   
  rocB = ta.ROC(df_new['Close'], timeperiod=10)
  #adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
  #mfi = ta.MFI(df['High'], df['Low'], df['Close'], df['Volume'], timeperiod=14)
  
  High = float(df['High'][-2])
  Low = float(df['Low'][-2])
  #Open = float(df['Open'][-1])
  diff = abs((High / Low -1) * 100)
  slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
  #atr = ta.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
  #tra = ta.TRANGE(df['High'], df['Low'], df['Close'])
  
  print(symbol)
 
  print(adx[-1])
 
       
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
   
        
  if (diff > 1):
    if (rsi[-2] < 20) and (slowk[-2] < 10):    
      requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=UNOLONG)
      Tb.telegram_canal_prueba( "⚡️ " + symbol + "\n🟢 LONG \n⏳ 3min \n💵 Precio: " + df['Close'][-1] + "\n🔝  Cambio: " + round(diff, 3) + " %" + "\n📈  RSI: " + round(rsi[-1], 3))
  if (diff > 1):
    if (rsi[-2] > 80) and (slowk[-2] > 90):   
      requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=UNOSHORT)  
      Tb.telegram_canal_prueba( "⚡️ " + symbol + "\n🔴 SHORT \n⏳ 3min \n💵 Precio: " + df['Close'][-1] + "\n🔝  Cambio: " + round(diff, 3) + " %" + "\n📉  RSI: " + round(rsi[-1], 3))
  
  
  return round(last_rsi, 1), rsi_stat

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
            
schedule.every(3).minutes.do(server_time)
  
while True:
    schedule.run_pending()
    ti.sleep(1)
