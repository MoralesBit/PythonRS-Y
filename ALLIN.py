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

intervals = [0, 3, 6, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57]
connection = ""
period = 14
 
def indicator(symbol):
  rsi_stat = ""
   
  kline = client.futures_historical_klines(symbol, "15m", "24 hours ago UTC+1",limit=500)
  df = pd.DataFrame(kline)
 
    
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'IGNORE',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
     
  rsi = ta.RSI(df["Close"], timeperiod=period)
 
  last_rsi = rsi   
  upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
 
  roc = ta.ROC(df['Close'], timeperiod=10)
  adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
  mfi = ta.MFI(df['High'], df['Low'], df['Close'], df['Volume'], timeperiod=14)
  df['EMA'] = ta.EMA(df['Close'], timeperiod = 13)
  df['MA50'] = df['Close'].ewm(span=45).mean()
  df['EMA200'] = ta.EMA(df['Close'], timeperiod = 200)
  df['EMA500'] = ta.EMA(df['Close'], timeperiod = 500)
  #df['ADV']=pd.mean(df['Volume'], window=9)
  
  #df_new = pd.DataFrame(bars, columns=['Open', 'High', 'Low', 'Close', 'Volume'])
  Close = float(df['Close'][-2])
  High = float(df['High'][-1])
  Low = float(df['Low'][-1])
  diff = abs((High / Low -1) * 100)
  #diff2 = abs((float(df['High'][-2]) / float(df['Low'][-2]) - 1) * 100)
  diff_M = abs((High - Close)/High)*100
  df['VolumeP'] = df['Volume'].ewm(span=10).mean()
  slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
  Open = float(df['Open'][-1])
  #df['MA100'] = df['Close'].ewm(span=100).mean()
  macd, signal, hist = ta.MACD(df['Close'], 
                                    fastperiod=12, 
                                    slowperiod=26, 
                                    signalperiod=9)
  
  #BB = ((float(df['Close'][-1]) - lowerband3[-1])/(upperband3[-1] - lowerband3[-1]))
  obv = ta.OBV(df['Close'], df['Volume'])
  ad = ta.AD(df['High'], df['Low'], df['Close'], df['Volume'])
  aroondown, aroonup = ta.AROON(df['High'], df['Low'], timeperiod=14)
  cci = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)
  #wma = ta.WMA() 
  #HMA = ma(2*ma(n/2) - ma(n)),sqrt(n)
  #ma = ta.MA()
  #var = taVAR()
    
  print(symbol)
     
  CCISHORT = {
  "name": "CCI SHORT",
  "secret": "w48ulz23f6",
  "side": "sell",
  "symbol": symbol
}
  CCILONG = {
  "name": "CCI LONG",
  "secret": "xxuxkqf0gpj",
  "side": "buy",
  "symbol": symbol
}
  
  if (cci[-3] < 0) and (cci[-2] > 0) and (Close > (df['MA50'][-1])) and ((df['MA50'][-2]) < (df['MA50'][-1])) and ( macd[-1] > signal[-1]) :
      requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=CCILONG)
      Tb.telegram_send_message( "🎱 " + symbol + "\n🟢 ALCISTA \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n⚠️ No Operar")
  elif (cci[-3] > 0) and (cci[-2] < 0) and (Close < (df['MA50'][-1])) and ((df['MA50'][-2]) > (df['MA50'][-1])) and ( macd[-1] < signal[-1]):
      requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CCISHORT)  
      Tb.telegram_send_message( "🎱 " + symbol + "\n🔴 BAJISTA \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n⚠️ No Operar")
    
  return round(last_rsi, 1), rsi_stat,  print(diff_M)

if __name__ == '__main__':
  monedas = client.futures_exchange_info()
  # 1. Obtener todas las monedas tradeables de futuros
  symbols = [
    symbol['symbol'] for symbol in monedas['symbols']
    if symbol['status'] == "TRADING"
  ]
#symbols = ["HIGHUSDT", "HOOKUSDT", "DUSKUSDT", "MINAUSDT","OPUSDT", "MASKUSDT"]

def server_time():
      
  time_server = client.get_server_time()
  time = pd.to_datetime(time_server["serverTime"], unit="ms")
  minute = int(time.strftime("%M"))
  second = int(time.strftime("%S"))
  
  for symbol in symbols:
    indicator(symbol)
    ti.sleep(1)
     
while (True):
  server_time()
  ti.sleep(1)
 
