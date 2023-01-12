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
  adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
  mfi = ta.MFI(df['High'], df['Low'], df['Close'], df['Volume'], timeperiod=14)
  df['EMA'] = ta.EMA(df['Close'], timeperiod = 30)
  #bars = client.futures_ticker()
  #df_new = pd.DataFrame(bars, columns=['Open', 'High', 'Low', 'Close', 'Volume'])
  Close = float(df['Close'][-1])
  High = float(df['High'][-1])
  Low = float(df['Low'][-1])
  diff = abs((High / Low -1) * 100)
  slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
  will = ta.WILLR(df['High'], df['Low'], df['Close'], timeperiod=14)
  
  #ma = ta.SMA(oh, timeperiod=3)
  
  CORTO = {
  "name": "CORTO EST 1 PORC",
  "secret": "w48ulz23f6",
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
  print(diff)
  #print(oh)
  #print(ma)
  #print(df_new['Volume'][-1])
  
  if (diff > 1) and (lowerband[-2] > Close) and (rsi[-2] < 30) and (slowk[-2] < 10):
    
    Tb.telegram_send_message(" ⚡️ " + symbol + "\n 🟢 LONG \n 💵 Precio: " + df['Close'][-1])
  elif (diff > 1) and (upperband[-2] < Close) and (rsi[-2] > 70) and (slowk[-2] > 90):
    requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CORTO)
    Tb.telegram_send_message(" ⚡️ " + symbol + "\n 🔴 SHORT \n 💵 Precio: " + df['Close'][-1])

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
    ti.sleep(0.15)
        
        
while (True):
  
  server_time()
