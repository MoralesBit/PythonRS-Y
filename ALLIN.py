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
  
  kline = client.futures_historical_klines(symbol, "15m", "6 hours ago UTC+1",limit=500)
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
   
  cci5 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=5)
  cci28 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=28)
  cci58 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=58)
  
  adxr = ta.ADXR(df['High'], df['Low'], df['Close'], timeperiod=14)
  
  adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
  
  roc = ta.ROC(df['Close'], timeperiod=10)
  
  rsi = ta.RSI(df["Close"], timeperiod=period)

  try:
    BB = round(((float(df['Close'][-2]) - df['lowerband'][-2])/(df['upperband'][-2] - df['lowerband'][-2])),2)
  except ZeroDivisionError:
    return 0.5
  

  info = client.futures_historical_klines("BTCUSDT", "15m", "24 hours ago UTC+1",limit=1000) 
  df_new = pd.DataFrame(info)
       
  if not df_new.empty:
        df_new.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close' 'IGNORE',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
  df_new['Date'] = pd.to_datetime(df_new['Date'], unit='ms')
  df_new = df_new.set_index('Date')
  cciB = ta.CCI(df_new['High'], df_new['Low'], df_new['Close'], timeperiod=28)
  macdB, signalB, histB = ta.MACD(df_new['Close'], 
                                    fastperiod=12, 
                                    slowperiod=26, 
                                    signalperiod=9)   
  rocB = ta.ROC(df_new['Close'], timeperiod=10)
  df_new['EMA200'] = df_new['Close'].ewm(200).mean()
 
  #adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
  #mfi = ta.MFI(df['High'], df['Low'], df['Close'], df['Volume'], timeperiod=14)
  
  #High = float(df['High'][-1])
  #Low = float(df['Low'][-1])
  #Open = float(df['Open'][-1])
  #diff = abs((High / Low -1) * 100)
  #slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
  #atr = ta.ATR(df['High'], df['Low'], df['Close'], timeperiod=14)
  #tra = ta.TRANGE(df['High'], df['Low'], df['Close'])
  
  print(symbol)
  print(BB)
         
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
    
  #EMA (mejorar)
        
  #if df['EMA200'][-2] < float(df['Close'][-2]) :
    #if (df['Positions'][-1] == 1.0) and (cci5[-1] > 0):
      #requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=CCILONG)
      #Tb.telegram_canal_prueba( "EMA 13-100: \n" + symbol + "\n🟢 LONG \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n EMA 13 " + str(round((df['EMA13'][-1]),3)) + "\n EMA 100: " + str(round((df['EMA100'][-1]),3)))
  #if df['EMA200'][-2] > float(df['Close'][-2]):     
    #if (df['Positions'][-1] == -1.0) and (cci5[-1] < 0):
      #requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CCISHORT)  
      #Tb.telegram_canal_prueba( "EMA 13-100: \n" + symbol + "\n🔴 SHORT \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n EMA 13 " + str(round((df['EMA13'][-1]),3)) + "\n EMA 100: " + str(round((df['EMA100'][-1]),3)))
  
  # fishing Pisha    
  if (float(BB) <= 0 ) and (float(BB) != "-inf" ) and (cci5[-2] < 0) and (cci5[-1] > 0):
      requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=PLONG)
      Tb.telegram_send_message( "⚡️ " + symbol + "\n🟢 LONG \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n📶 BB : " + str(BB) + " \n⚠️ No Operar \n📈 Fishing Pisha")
       
  if (float(BB) >= 1) and (float(BB) != "-inf" ) and (cci5[-2] > 0) and (cci5[-1] < 0):
      requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=PSHORT)  
      Tb.telegram_send_message( "⚡️ " + symbol + "\n🔴 SHORT \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n📶 BB : " + str(BB)+ "\n⚠️ No Operar \n📉 Fishing Pisha")
  elif (float(BB) == "-inf" ):
        print ("Zero")
   #Top Trend  
  if (cci58[-2] < 0) and (cci58[-1] > 0) and (hist[-1] > 0):
      if (adxr[-1] > 25):
        #requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=TOPLONG)
        Tb.telegram_canal_prueba( "⚡️ " + symbol + "\n🟢 LONG \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n⚠️ No Operar \n📈 Top Trend")
       
  if  (cci58[-2] > 0) and (cci58[-1] < 0) and (hist[-1] < 0):
      if (adxr[-1] > 25):
        #requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=TOPSHORT)  
        Tb.telegram_canal_prueba( "⚡️ " + symbol + "\n🔴 SHORT \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n⚠️ No Operar \n📉 Top Trend")
          
  #Master Trend  
  if (cciB[-2] < 0) and (cciB[-1] > 0) and (histB[-1] > 0):
      if (cci5[-1] > 0) and (adxr[-1] > 25):
        requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=CCILONG)
        Tb.telegram_send_message( "⚡️ " + symbol + "\n🟢 LONG \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n⚠️ No Operar \n📈 Master Trend")
       
  if  (cciB[-2] > 0) and (cciB[-1] < 0) and (histB[-1] < 0):
      if (cci5[-1] < 0) and (adxr[-1] > 25):
        requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CCISHORT)  
        Tb.telegram_send_message( "⚡️ " + symbol + "\n🔴 SHORT \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n⚠️ No Operar \n📉 Master Trend")     

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
            
schedule.every(15).minutes.at(":05").do(server_time)
  
while True:
    schedule.run_pending()
    ti.sleep(1)   
