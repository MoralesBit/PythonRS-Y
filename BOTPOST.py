from binance.client import Client
import pandas as pd
import numpy
import talib as ta
import Telegram_bot as Tb
import  schedule as schedule
import time as ti
import requests


Pkey = ''
Skey = ''

client = Client(api_key=Pkey, api_secret=Skey)

intervals = [
  0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57
]
connection = ""
period = 14
def indicator(symbol):
  rsi_stat = ""
  kline = client.futures_historical_klines(symbol, "3m", "2 hours ago UTC+1",limit=100)
  df = pd.DataFrame(kline)
  if not df.empty:
    df.columns = [
      'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'IGNORE',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x'
    ]
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
  rsi = ta.RSI(df["Close"], timeperiod=period)
  last_rsi = rsi[-2]
    
  upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=3,
                                               nbdevdn=3,
                                               matype=0)
  roc = ta.ROC(df['Close'], timeperiod=10)
  Open = float(df['Open'][-1])
  Close = float(df['Close'][-2])
  diff = abs((High / Low -1) * 100)
  slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
  High = float(df['High'][-1])
    
  CORTO = {
  "name": "USUARIO 002 - CORTO",
  "secret": "hgw3399vhh",
  "side": "sell",
  "symbol": symbol,
  "open": { "price": "" }
  }
  LARGO = {
  "name": "USUARIO 002 - LARGO",
  "secret": "xjth0i3qgb",
  "side": "buy",
  "symbol": symbol
  }
 
  print(symbol)
   
  if Close == Open:
    if (diff > 3) and (rsi[-2] < 20) and (slowk[-2] < 20) and (lowerband[-2] >= Close):
      requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=LARGO)
      Tb.telegram_send_message(" ⚡️ " + symbol + "\n 🌵 LONG \n 💵 Precio: " + df['Close'][-1] + "\n 🔃 % ROC: " + str(round(roc[-1],2)) + "\n 📉 RSI : " + str(round(rsi[-1],2)))
    elif (diff > 3) and (rsi[-2] > 80) and (slowk[-2] < 80) and (upperband[-2] < Close):
      requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=CORTO)
      Tb.telegram_send_message(" ⚡️ " + symbol + "\n 🩸 SHORT \n 💵 Precio: " + df['Close'][-1] + "\n 🔃 % ROC: " + str(round(roc[-1],2)) + "\n 📈 RSI : " + str(round(rsi[-1],2)))

  return round(last_rsi, 1), rsi_stat

if __name__ == '__main__':
  monedas = client.futures_exchange_info()
  # 1. Obtener todas las monedas tradeables de futuros
  symbols = [
    symbol['symbol'] for symbol in monedas['symbols']
    if symbol['status'] == "TRADING"
  ]
#symbols = ["BTCUSDT", "TRXUSDT", "BNBUSDT", "ETHUSDT", "ETCUSDT", "MATICUSDT", "XRPUSDT", "AVAXUSDT", "DOGEUSDT", "ADAUSDT"]

def server_time():
  
  for symbol in symbols:
    indicator(symbol)
    ti.sleep(0.01)
        
   
while (True):
  
  server_time()
  ti.sleep(120)
  
