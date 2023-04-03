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
   
  df['First_cross'] = np.where((float(df['Close'][-2])) > (df['first_level']),1,0)
  df['Secound_cross'] = np.where((float(df['Close'][-2])) > (df['secound_level']),1,0)
  df['third_cross'] = np.where((float(df['Close'][-2])) > (df['third_level']),1,0)
  df['Fourth_cross'] = np.where((float(df['Close'][-2])) > (df['fourth_level']),1,0)
  
    

    
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
    
   # FIBO + RSI - contratendica.
  if (rsi[-3] < 30) and (rsi[-2] > 30):
    if (df['First_cross'][-2] == 1):
          Tb.telegram_canal_prueba(f"💎 {symbol}\n🟢 LONG\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📈 TREND_FI + RSI")
    elif (df['Secound_cross'][-2] == 1):
          Tb.telegram_canal_prueba(f"💎 {symbol}\n🟢 LONG\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📈 TREND_FI + RSI")  
    elif (df['third_cross'][-2] == 1):
          Tb.telegram_canal_prueba(f"💎 {symbol}\n🟢 LONG\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📈 TREND_FI + RSI")  
    elif (df['Fourth_cross'][-2] == 1):
          Tb.telegram_canal_prueba(f"💎 {symbol}\n🟢 LONG\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📈 TREND_FI + RSI")  
  
  if (rsi[-3] > 70) and (rsi[-2] < 70): 
    if (df['First_cross'][-2] == 0):
          Tb.telegram_canal_prueba(f"💎 {symbol}\n🔴 SHORT\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📉 TREND_FI + RSI")
    elif (df['Secound_cross'][-2] == 0):
          Tb.telegram_canal_prueba(f"💎 {symbol}\n🔴 SHORT\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📉 TREND_FI + RSI")
    elif (df['third_cross'][-2] == 0):
          Tb.telegram_canal_prueba(f"💎 {symbol}\n🔴 SHORT\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📉 TREND_FI + RSI")
    elif (df['Fourth_cross'][-2] == 0):
          Tb.telegram_canal_prueba(f"💎 {symbol}\n🔴 SHORT\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📉 TREND_FI + RSI")
     
   # FIBO + MACD
  if (df['tendencia'][-2] == 1) and (df['tendenciaemas'][-2] == 1) and (df['macd'][-3] <  df['macd_signal'][-3]) and (df['macd'][-2] > df['macd_signal'][-2]):
    if (df['First_cross'][-2] == 1):
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📈 TREND_FI")
    elif (df['Secound_cross'][-2] == 1):
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📈 TREND_FI") 
    elif (df['third_cross'][-2] == 1):
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📈 TREND_FI") 
    elif (df['Fourth_cross'][-2] == 1):
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📈 TREND_FI")
  
  if (df['tendencia'][-2] == 0) and (df['tendenciaemas'][-2] == 0) and  (df['macd'][-3] >  df['macd_signal'][-3]) and (df['macd'][-2] < df['macd_signal'][-2]):
    if (df['First_cross'][-2] == 0):
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📉 TREND_FI")
    elif (df['Secound_cross'][-2] == 0):
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📉 TREND_FI")
    elif (df['third_cross'][-2] == 0):
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📉 TREND_FI") 
    elif (df['Fourth_cross'][-2] == 0):
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3min\n💵 Precio: {df['Close'][-1]}\n📉 TREND_FI") 
  
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

  print(symbol)
  print(df['first_level'][-2])
  print(df['secound_level'][-2])
  print(df['third_level'][-2])
  print(df['fourth_level'][-2])
  
 
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
            
#schedule.every(3).minutes.at(":01").do(server_time)
  
while True:
    server_time()
    #schedule.run_pending()
    ti.sleep(1)
