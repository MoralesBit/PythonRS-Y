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
period2 = 13
 

def indicator(symbol):
  rsi_stat = ""
  kline5 = client.futures_historical_klines(symbol, "15m", "24 hours ago UTC+1",limit=500) 
  kline = client.futures_historical_klines(symbol, "3m", "24 hours ago UTC+1",limit=500)
  df = pd.DataFrame(kline)
  df_new = pd.DataFrame(kline5)
    
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'IGNORE',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
    
    if not df_new.empty:  
      df_new.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'IGNORE',
        'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
      df_new['Date'] = pd.to_datetime(df_new['Date'], unit='ms')
      df_new = df_new.set_index('Date')
    
  rsi = ta.RSI(df["Close"], timeperiod=period)
  rsi2 = ta.RSI(df["Close"], timeperiod=period2)
  last_rsi = rsi   
  upperband3, middleband3, lowerband3 = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
  upperband5, middleband5, lowerband5 = ta.BBANDS(df_new['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
  roc = ta.ROC(df['Close'], timeperiod=10)
  adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
  mfi = ta.MFI(df['High'], df['Low'], df['Close'], df['Volume'], timeperiod=14)
  df['EMA'] = ta.EMA(df['Close'], timeperiod = 13)
  df_new['MA50'] = df_new['Close'].ewm(span=50).mean()
  df['EMA200'] = ta.EMA(df['Close'], timeperiod = 200)
  df['EMA500'] = ta.EMA(df['Close'], timeperiod = 500)
  #df['ADV']=pd.mean(df['Volume'], window=9)
  
  #df_new = pd.DataFrame(bars, columns=['Open', 'High', 'Low', 'Close', 'Volume'])
  Close = float(df['Close'][-1])
  Close15 = float(df_new['Close'][-1])
  High = float(df['High'][-1])
  Low = float(df['Low'][-1])
  diff = abs((High / Low -1) * 100)
  #diff2 = abs((float(df['High'][-2]) / float(df['Low'][-2]) - 1) * 100)
  diff_M = abs((High - Close)/High)*100
  df['VolumeP'] = df['Volume'].ewm(span=10).mean()
  slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
  slowk15, slowd15 = ta.STOCH(df_new['High'], df_new['Low'], df_new['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
  Open = float(df['Open'][-1])
  #df['MA100'] = df['Close'].ewm(span=100).mean()
  macd, signal, hist = ta.MACD(df['Close'], 
                                    fastperiod=12, 
                                    slowperiod=26, 
                                    signalperiod=9)
  macd15, signal15, hist15 = ta.MACD(df_new['Close'], 
                                    fastperiod=12, 
                                    slowperiod=26, 
                                    signalperiod=9)
  #BB = ((float(df['Close'][-1]) - lowerband3[-1])/(upperband3[-1] - lowerband3[-1]))
  obv = ta.OBV(df['Close'], df['Volume'])
  ad = ta.AD(df['High'], df['Low'], df['Close'], df['Volume'])
  aroondown, aroonup = ta.AROON(df['High'], df['Low'], timeperiod=14)
  cci = ta.CCI(df_new['High'], df_new['Low'], df_new['Close'], timeperiod=20)
  #wma = ta.WMA() 
  #HMA = ma(2*ma(n/2) - ma(n)),sqrt(n)
  #ma = ta.MA()
  #var = taVAR()
  
  
  print(symbol)
  
     
  CORTOT = {
  "name": "TENDENCIA-SHORT",
  "secret": "hgw3399vhh",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": ""
  }
}
  LARGOT= {
  "name": "TENDENCIA-LONG",
  "secret": "xjth0i3qgb",
  "side": "buy",
  "symbol": symbol
} 
  SHORT1P = {
  "name": "STOC 5 MIN SHORT",
  "secret": "azsdb9x719",
  "side": "sell",
  "symbol": symbol
} 
  LONG1P = {
  "name": "STOC 5 MIN LONG",
  "secret": "0kivpja7tz89",
  "side": "buy",
  "symbol": symbol
}  

  CORTO = {
  "name": "CORTO EST 1 PORC",
  "secret": "w48ulz23f6",
  "side": "sell",
  "symbol": symbol
}
  
  LARGO = {
  "name": "LARGO EST 1 PORC",
  "secret": "xxuxkqf0gpj",
  "side": "buy",
  "symbol": symbol
}
  
  U003S = {
  "name": "CORTO1%",
  "secret": "uluh5jwl0p",
  "side": "sell",
  "symbol": symbol
}
  
  U003L = {
  "name": "LARGO1%",
  "secret": "zhbg0ei79jg",
  "side": "buy",
  "symbol": symbol
}
  
  U004S  = {
  "name": "CORTO",
  "secret": "cutm8ggcvde",
  "side": "sell",
  "symbol": symbol
}
  
  U008S  = {
  "name": "BOT SHORT 1%",
  "secret": "bv6nraz31sn",
  "side": "sell",
  "symbol": symbol
}
  
  U009S  = {
  "name": "BOT SHORT 1%",
  "secret": "hyrk4rb79rk",
  "side": "sell",
  "symbol": symbol
}
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

#Copia Merlin
  if diff_M != 0:
    if (diff > 3) and (diff_M < 0.20) and (Close > upperband3[-1]) and (slowk[-1] > 70):
        #requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=MSHORT)
        Tb.telegram_send_message( symbol + "\n 🔴 SHORT \n 💵 Precio: " + df['Close'][-1] + " Mechazo \n")
    elif (diff > 3) and (diff_M < 0.20) and (Close < lowerband3[-1]) and (slowk[-1] < 30):
        #requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=MLARGO)
        Tb.telegram_send_message( symbol + "\n 🟢 LONG \n 💵 Precio: " + df['Close'][-1] + " Mechazo \n")
  else:
    print(diff_M)
  
  #30 MINUTOS PYTHON
 
  if (float(df_new['Close'][-2]) > upperband5[-2]) and (rsi2[-2] > 80) and (slowk15[-2] > 95) and (cci[-1] > 180):
        requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=SHORT1P)
        Tb.telegram_send_message( symbol + "\n 🔴 SHORT \n 💵 Precio: " + df['Close'][-1] + "\n ESTOCASTICO +\n RSI 15 MINUTOS")
  elif (float(df_new['Close'][-2]) > lowerband5[-2]) and (rsi2[-2] < 20) and (slowk15[-2] < 5) and (cci[-1] <-180):
        requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=LONG1P)
        Tb.telegram_send_message( symbol + "\n 🟢 LONG \n 💵 Precio: " + df['Close'][-1] + "\n ESTOCASTICO +\n RSI 15 MINUTOS")
  
  #TENDENCIA EN 3 MIN CUANDO BTC HACE PUM:
  #if  (float(df['VolumeP'][-1]) < float(df['Volume'][-1])) and (macd[-2] > signal[-2]) and (signal[-1] > macd[-1]) and (hist[-2] > 0) and (hist[-1] < 0) and (cci[-1] < 0) and (rsi[-1] < 40) and (rsi[-1] > 30):
      #Tb.telegram_send_message( " ⚡️ " + symbol + "\n 🔴 SHORT \n 💵 Precio: " + df['Close'][-1] + "\n Tendencia ")
      #requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=CORTOT)
  #elif (cci[-1] > 180) and (float(df['VolumeP'][-1]) < float(df['Volume'][-1])) and (macd[-2] < signal[-2]) and (signal[-1] < macd[-1]) and (hist[-2] < 0) and (hist[-1] > 0) and (cci[-1] > 0) and (rsi[-1] > 60) and (rsi[-1] < 70):
      #Tb.telegram_send_message( " ⚡️ " + symbol + "\n 🟢 LONG \n 💵 Precio: " + df['Close'][-1] + "\n Tendencia")
      #requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=LARGOT)
  
  #Tendicia con CCI
  
  #if (cci[-2] < 0) and (cci[-1] > 0) and (Close15 > df_new['MA50'][-1]) and  (hist15[-2] < hist15[-1]) and (slowk15[-2] < slowk15[-1]):
      #requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=CCILONG)
      #Tb.telegram_send_message( "🎱 " + symbol + "\n🟢 Alcista \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n⚠️ No Operar")
  #elif (cci[-2] > 0) and (cci[-1] < 0) and (Close15 < df_new['MA50'][-1]) and (hist15[-2] > hist15[-1]) and (slowk15[-2] > slowk15[-1]):
      #requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CCISHORT)  
      #Tb.telegram_send_message( "🎱 " + symbol + "\n🔴 Bajista \n⏳ 15min \n💵 Precio: " + df['Close'][-1] + "\n⚠️ No Operar")

    #Alertas 1% BOT
  if (roc[-1] < -1.5) and (diff > 1) and (lowerband3[-2] > Close) and (rsi[-2] < 30) and (slowk[-2] < 5):
    requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=LARGO)
    requests.post('https://hook.finandy.com/fc5QlbF36Dekt67GqFUK', json=U003L)
    Tb.telegram_send_message(" ⚡️ " + symbol + "\n 🟢 LONG \n 💵 Precio: " + df['Close'][-1])
  elif (roc[-1] > 1.5) and (diff > 1) and (upperband3[-2] < Close) and (rsi[-2] > 70) and (slowk[-2] > 95):
    requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CORTO)
    requests.post('https://hook.finandy.com/Xk9inkBl1iEVw-reqFUK', json=U003S)
    requests.post('https://hook.finandy.com/r5cQN9H916sGrlFmqFUK', json=U004S)
    Tb.telegram_send_message(" ⚡️ " + symbol + "\n 🔴 SHORT \n 💵 Precio: " + df['Close'][-1])
  
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
          ti.sleep(0.05)
     
while (True):
  server_time()  
