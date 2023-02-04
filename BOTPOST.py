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
  kline = client.futures_historical_klines(symbol, "5m", "2 hours ago UTC+1",limit=100)
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
  df['EMA'] = ta.EMA(df['Close'], timeperiod = 30)
  #bars = client.futures_ticker()
  #df_new = pd.DataFrame(bars, columns=['Open', 'High', 'Low', 'Close', 'Volume'])
  Close = float(df['Close'][-1])
  High = float(df['High'][-1])
  Low = float(df['Low'][-1])
  diff = abs((High / Low -1) * 100)
  slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
  Open = float(df['Open'][-1])
  df['MA100'] = df['Close'].ewm(span=100).mean()
  df['MA13'] = df['Close'].ewm(span=13).mean()
  macd, signal, hist = ta.MACD(df['Close'], 
                                    fastperiod=12, 
                                    slowperiod=26, 
                                    signalperiod=9)
  
  #BB = ((Close - lowerband[-1])/(upperband[-1] - lowerband[-1])) 
  
  print(symbol)
 
  
  SHORT = {
  "name": "EMA 13-100 SHORT",
  "secret": "hgw3399vhh",
  "side": "sell",
  "symbol": symbol
}

  LONG = {
  "name": "EMA 13-100 LONG",
  "secret": "xjth0i3qgb",
  "side": "buy",
  "symbol": symbol
}
    
  if (df['MA13'][-1] < df['MA100'][-1]) and (df['MA100'][0] < df['MA13'][0]) and (macd[-1] < macd[0]):
      requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=LONG)
      Tb.telegram_send_message(" Cruce EMA 13-100 " + symbol + "\n 🟢 LONG \n 💵 Precio: " + df['Close'][-1])
  elif (df['MA13'][-1] > df['MA100'][-1]) and (df['MA100'][0] > df['MA13'][0]) and (macd[-1] > macd[0]):
      requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=SHORT)  
      Tb.telegram_send_message(" Cruce EMA 13-100 " + symbol + "\n 🔴 SHORT \n 💵 Precio: " + df['Close'][-1])

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
    ti.sleep(0.1)
        
        
while (True):
  
  server_time()
  ti.sleep(60)

  
