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
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
  roc = ta.ROC(df['Close'], timeperiod=10)
  
  #bars = client.futures_ticker()
  #df_new = pd.DataFrame(bars, columns=['Open', 'High', 'Low', 'Close', 'Volume'])
    
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
  print(rsi[-2:].values[0])
  print(rsi[-1:].values[0])
  print(roc[-1])
  #print(df_new['Volume'][-1])
  
  if (rsi[-2:].values[0] < 25) and (rsi[-1:].values[0] > 25) and (roc[-1] < -3):
    requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=LARGO)
    Tb.telegram_send_message(" ⚡️ " + symbol + "\n 🌵 LONG \n 💵 Precio: " + df['Close'][-1] + "\n 🔃 % ROC: " + str(round(roc[-1],2)) + "\n 📉 RSI : " + str(round(rsi[-1],2)))
  elif (rsi[-2:].values[0] > 75) and (rsi[-1:].values[0] < 75) and (roc[-1] > 3):
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

  for symbol in symbols:
    indicator(symbol)
    ti.sleep(2)
