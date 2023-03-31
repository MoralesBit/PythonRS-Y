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
  
  cci3 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=3)
  cci20 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)
  cci28 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=28)
  cci58 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=58)
  
  adxr = ta.ADXR(df['High'], df['Low'], df['Close'], timeperiod=14)
  adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
  slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
  df['Will'] = ta.WILLR(df['High'], df['Low'], df['Close'], timeperiod=14)
  df['BBW'] = (df['upperband'] - df['lowerband']) / df['middleband']  
  chain = ta.ADOSC(df['High'], df['Low'], df['Close'], df['Volume'], fastperiod=3, slowperiod=10)
 
  df['EMA200'] = df['Close'].ewm(200).mean()
  df['EMA100'] = df['Close'].ewm(100).mean()
  
  df['tendencia'] = np.where((float(df['Close'][-2])) > (df['EMA100'][-2]),1,0)
  df['tendenciaemas'] = np.where(df['EMA100'][-2] > (df['EMA200'][-2]),1,0)
  
  info = client.futures_historical_klines("BTCUSDT", "15m", "2 days ago UTC+1",limit=1000) 
  df_new = pd.DataFrame(info)
       
  if not df_new.empty:
        df_new.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close' 'IGNORE',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
  df_new['Date'] = pd.to_datetime(df_new['Date'], unit='ms')
  df_new = df_new.set_index('Date')
  
  cciB = ta.CCI(df_new['High'], df_new['Low'], df_new['Close'], timeperiod=20)
  cciB58 = ta.CCI(df_new['High'], df_new['Low'], df_new['Close'], timeperiod=58)
  
  df_new['EMA200B'] = df_new['Close'].ewm(200).mean()
  
  df_new['tendenciaB'] = np.where((float(df_new['Close'][-2])) > (df_new['EMA200B'][-2]), 1,0)
  
  
    
  print(symbol)
  print(df['EMA100'][-2])
  print(df['EMA200'][-2])
  
    
  MINIFSHORT = {
  "name": "SHORT-MINIFISH",
  "secret": "w48ulz23f6",
  "side": "sell",
  "symbol": symbol
  }
  MINIFLONG = {
  "name": "LONG-MINIFISH",
  "secret": "xxuxkqf0gpj",
  "side": "buy",
  "symbol": symbol
  }
     
  TRENDSHORT = {
  "name": "SHORT-TREND",
  "secret": "hgw3399vhh",
  "side": "sell",
  "symbol": symbol
  }
  TRENDLONG = {
  "name": "LONG-TREND",
  "secret": "xjth0i3qgb",
  "side": "buy",
  "symbol": symbol
  }
  
  
  # DIAMOND
  if (df['tendencia'][-2] == 1) and (df['tendenciaemas'][-2] == 1):
    if (rsi[-3] < 40) and (rsi[-2] > 40) and (df['macd_hist'][-2] < 0) and (adxr[-2] > 20) and (cci58[-2] > 0):   
        #requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=DIAMONDLONG)
        Tb.telegram_canal_prueba(f"💎 {symbol}\n🟢 LONG\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📈 Diamond")
    
  # SHORT
  if (df['tendencia'][-2] == 0) and (df['tendenciaemas'][-2] == 0):
    if (rsi[-3] > 60) and (rsi[-2] < 60) and (df['macd_hist'][-2] > 0) and (adxr[-2] > 20) and (cci58[-2] < 0): 
       #requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=DIAMONDSHORT)  
       Tb.telegram_canal_prueba(f"💎 {symbol}\n🔴 SHORT\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📉 Diamond")
 
  
  
  #LONG Y SHORT > 50 - MINI FISHING 
  if (df['macd'][-3] >  df['macd_signal'][-3]) and (df['macd'][-2] < df['macd_signal'][-2]): 
    if (cci58[-2] > 0) and (rsi[-3] < 60) and (rsi[-2] > 60):     
      requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=MINIFLONG)
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📈  Mini FIshing")
    
  #LONG Y SHORT > 50 - MINI FISHING 
  if  (df['macd'][-3] <  df['macd_signal'][-3]) and (df['macd'][-2] > df['macd_signal'][-2]): 
   
    if (cci58[-2] < 0) and (rsi[-3] > 40) and (rsi[-2] < 40):  
      requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=MINIFSHORT)  
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📉  Mini FIshing")
 
   
 
  #FUNCIONA ESTABLE:
  
  #if (macdB[-2] > signalB[-2]) and (macdB[-3] < macdB[-2]): 
    #if (cci20[-3] < 0) and (cci20[-2] > 0) and (adxr[-3] < adxr[-2]) and (df['macd_hist'][-3] < df['macd_hist'][-2]) and (adx[-2] >= 20):    
      #requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=UNOLONG)
      #Tb.telegram_send_message(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📈  Fast Trend")
  #if (macdB[-2] < signalB[-2]) and (macdB[-3] > macdB[-2]): 
    #if (cci20[-3] > 0) and (cci20[-2] < 0) and (adxr[-3] < adxr[-2]) and (df['macd_hist'][-3] > df['macd_hist'][-2]) and (adx[-2] >= 20):   
      #requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=UNOSHORT)  
      #Tb.telegram_send_message(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📉  Fast Trend")
  
  # Tendencia 100 y 200(LONG)
  if (df['tendencia'][-2] == 1) and (df['tendenciaemas'][-2] == 1):
    if (df['macd'][-3] <  df['macd_signal'][-3]) and (df['macd'][-2] > df['macd_signal'][-2]) and (adx[-3] < adx[-2] > 20) and (df['BBW'][-2] > 0.02):   
      requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=TRENDLONG)
      Tb.telegram_send_message(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📈 Trend")
    
  # SHORT
  if (df['tendencia'][-2] == 0) and (df['tendenciaemas'][-2] == 0):
    if (df['macd'][-3] >  df['macd_signal'][-3]) and (df['macd'][-2] < df['macd_signal'][-2]) and (adx[-3] < adx[-2] > 20) and (df['BBW'][-2] > 0.02): 
      requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=TRENDSHORT)  
      Tb.telegram_send_message(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📉 Trend")
 
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
