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
period = 14

def indicator(symbol):
  
  kline = client.futures_historical_klines(symbol, "15m", "2 days ago UTC+1",limit=1000)
  df = pd.DataFrame(kline)
  
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
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
  
  df['upperband'], df['middleband'], df['lowerband'] = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
  macd, signal, hist = ta.MACD(df['Close'], 
                                    fastperiod=12, 
                                    slowperiod=26, 
                                    signalperiod=9)
  cci3 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=3) 
  cci5 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=5)
  cci14 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=14)
  cci20 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)
  cci28 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=28)
  cci58 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=58)
  
  adxr = ta.ADXR(df['High'], df['Low'], df['Close'], timeperiod=14)
  
  adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
  
  roc = ta.ROC(df['Close'], timeperiod=10)
  
  rsi = ta.RSI(df["Close"], timeperiod=period)
  rsi4 = ta.RSI(df["Close"], timeperiod=4)
  rsi5 = ta.RSI(df["Close"], timeperiod=5)
  
     
  #BBtop1 = (float(df['Close'][-1]) - df['lowerband'][-1])
  #BBdown1 = (df['upperband'][-1] - df['lowerband'][-1])
  
  df['tendencia'] = np.where((float(df['Close'][-1])) > (df['EMA200'][-1]), 1,0)
  
  info = client.futures_historical_klines("BTCUSDT", "15m", "2 days ago UTC+1",limit=1000) 
  df_new = pd.DataFrame(info)
       
  if not df_new.empty:
        df_new.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close' 'IGNORE',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
  df_new['Date'] = pd.to_datetime(df_new['Date'], unit='ms')
  df_new = df_new.set_index('Date')
  cciB = ta.CCI(df_new['High'], df_new['Low'], df_new['Close'], timeperiod=28)
  cciB58 = ta.CCI(df_new['High'], df_new['Low'], df_new['Close'], timeperiod=58)
  macdB, signalB, histB = ta.MACD(df_new['Close'], 
                                    fastperiod=12, 
                                    slowperiod=26, 
                                    signalperiod=9)   
  
  df_new['EMA200'] = df_new['Close'].ewm(200).mean()
 
    
  print(symbol)
  
             
  CCISHORT = {
  "name": "CCI SHORT",
  "secret": "w48ulz23f6",
  "side": "sell",
  "symbol": symbol
  }
  
  PSHORT = {
  "name": "PRUEBA SHORT",
  "secret": "azsdb9x719",
  "side": "sell",
  "symbol": symbol
  }
  CCILONG = {
  "name": "CCI LONG",
  "secret": "xxuxkqf0gpj",
  "side": "buy",
  "symbol": symbol
  }
  
  PLONG = {
  "name": "PRUEBA LONG",
  "secret": "0kivpja7tz89",
  "side": "buy",
  "symbol": symbol
  }
         
  #Bouncy
  if (cci14[-2] > 100) and (cci14[-1] < 100) and (rsi4[-1] > 60):
      #requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=PLONG)
      Tb.telegram_canal_prueba( "⚡️ " + symbol + "\n🟢 LONG \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\nBOUNCY")
  
  if (cci14[-2] < -100) and (cci14[-1] > -100) and (rsi4[-1] < 40):
      Tb.telegram_canal_prueba( "⚡️ " + symbol + "\n🔴 SHORT \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\nBOUNCY")
  
  #Bouncy
  if (df['tendencia'][-1] == 1):
    if (rsi5[-2] < 30 < rsi5[-1]) and (rsi[-1] < 40): 
      requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=PLONG)
      Tb.telegram_canal_prueba( "⚡️ " + symbol + "\n🟢 LONG \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\nFast Trend 15")
  
  # Fishing Pisha Nuevo 
  #LONG FISHING
  
  if (cci14[-2] > 100) and (cci14[-1] < 100) and (rsi4[-1] > 60):    
      requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=PLONG)
      Tb.telegram_send_message( "⚡️ " + symbol + "\n🟢 LONG \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n🎣 Fishing Pisha")
  
  #SHORT FISHING
  if (df['tendencia'][-1] == 0):
    if (cci14[-2] > 0) and (cci14[-1] < 0) and (rsi4[-1] < 30) and (rsi[-1] < 50):  
      requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=PSHORT)  
      Tb.telegram_send_message( "⚡️ " + symbol + "\n🔴 SHORT \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n🎣 Fishing Pisha")
  
  #Master Trend  
  if (cciB[-2] < 0) and (cciB[-1] > 0) and (df['tendencia'][-1] == 1) and (histB[-1] > 0):
      if (cci5[-1] > 0) and (rsi[-1] < 30):
        requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=CCILONG)
        Tb.telegram_send_message( "⚡️ " + symbol + "\n🟢 LONG \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n📈 Master Trend")
       
  if  (cciB[-2] > 0) and (cciB[-1] < 0) and (df['tendencia'][-1] == 0) and (histB[-1] < 0):
      if (cci5[-1] < 0) and (rsi[-1] > 70):
        requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CCISHORT)  
        Tb.telegram_send_message( "⚡️ " + symbol + "\n🔴 SHORT \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n📉 Master Trend")     

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
            
schedule.every(5).minutes.at(":01").do(server_time)
  
while True:
    #server_time()
    schedule.run_pending()
    ti.sleep(1)   
