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
  adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
  mfi = ta.MFI(df['High'], df['Low'], df['Close'], df['Volume'], timeperiod=14)
  ema = ta.EMA(df['Close'], timeperiod=50)
  #bars = client.futures_ticker()
  #df_new = pd.DataFrame(bars, columns=['Open', 'High', 'Low', 'Close', 'Volume'])
    
  CORTO = {
  "name": "PUM SHORT",
  "secret": "sa19z0p2jl",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": ""
  }
}

  LARGO = {
  "name": "PUM LONG",
  "secret": "y6e5h7q67w",
  "side": "buy",
  "symbol": symbol,
  "open": {
    "price": ""
  }
}
  print(symbol)
  print(rsi[-1:].values[0])
   
  #print(df_new['Volume'][-1])
  
  if (rsi[-2:].values[0] > 25) and (rsi[-1:].values[0] < 25) and (mfi[-2] > 20) and (mfi[-1] < 20) and (adx[-2] < 23) and (adx[-1] > 23) and (roc[-1] < -1):
    requests.post('https://hook.finandy.com/yOiR__CztpkFLaRKqFUK', json=CORTO)
    Tb.telegram_send_message(" 🔴 SHORT  " + symbol + "\n 💵 Precio: " + df['Close'][-1])
  elif (rsi[-2:].values[0] < 75) and (rsi[-1:].values[0] > 75) and (mfi[-2] < 80) and (mfi[-1] > 80) and (adx[-2] < 23) and (adx[-1] > 23) and (roc[-1] < 1):
    requests.post('https://hook.finandy.com/A81ci3iO7HXP9btKqFUK', json=LARGO)
    Tb.telegram_send_message(" 🟢 LONG  " + symbol + "\n 💵 Precio: " + df['Close'][-1])
    

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
    ti.sleep(0.25)
        
        
while (True):
  
  server_time()
