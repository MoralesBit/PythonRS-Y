from binance.client import Client
import pandas as pd
import talib as ta
import Telegram_bot as Tb
import  schedule as schedule
import time as ti
import requests
import numpy as np

Pkey = ''
Skey = ''

client = Client(api_key=Pkey, api_secret=Skey)

futures_info = client.futures_exchange_info()

symbols = [
    symbol['symbol'] for symbol in futures_info['symbols']
    if symbol['status'] == "TRADING"
  ]

def indicator(symbol):
  
  kline = client.futures_historical_klines(symbol, "3m", "24 hours ago UTC+1",limit=500)
  df = pd.DataFrame(kline)
  
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
    
    rsi = ta.RSI(df["Close"], timeperiod=14)
    Close = float(df['Close'][-2])
    Close_3 = float(df['Close'][-3])
    High = float(df['High'][-2])
    Low = float(df['Low'][-2])
    Open = float(df['Open'][-2])
    diff = abs((High / Low -1) * 100)
#    diff_high = abs((High / Close -1)*100)
#    diff_low = abs((Low / Close -1)*100)
    df['ema_13'] = df['Close'].ewm(span=13, adjust=False).mean()
    df['ema_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    cci_20 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)
#    slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
   
    
    
    upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
   
     # Calcula el precio máximo y mínimo
    high_price = np.max(df['Close'])
    low_price = np.min(df['Close'])
    
    #noro strategy
    var = 0.85
    ma = ta.SMA(df['Close'], timeperiod=3)
    long = ma + ((ma / 100) *(-var))
    short = ma + ((ma / 100) *(var))
       
    
    enter = Close*(0.98)
    info = client.futures_historical_klines("BTCUSDT", "15m", "2 days ago UTC+1",limit=1000) 
    df_new = pd.DataFrame(info)
       
    if not df_new.empty:
        df_new.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close' 'IGNORE',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df_new['Date'] = pd.to_datetime(df_new['Date'], unit='ms')
    df_new = df_new.set_index('Date')
    cciB = ta.CCI(df_new['High'], df_new['Low'], df_new['Close'], timeperiod=28)
    
    
    PORSHORT = {
    "name": "CORTO 3POR",
    "secret": "ao2cgree8fp",
    "side": "sell",
    "symbol": symbol,
    "open": {
    "price": Close
    }
    }
    PORLONG = {
    "name": "LARGO 3POR",
    "secret": "nwh2tbpay1r",
    "side": "buy",
    "symbol": symbol,
    "open": {
    "price": Close
    }
    }
    
    PICKERSHORT= {
  "name": "PICKER SHORT",
  "secret": "hgw3399vhh",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": Close
  }
}
    PICKERLONG = {
  "name": "PICKER LONG",
  "secret": "xjth0i3qgb",
  "side": "buy",
  "symbol": symbol,
  "open": {
    "price": Close
  }
}
    
    CARLOSSHORT = {
  "name": "Hook 200276",
  "secret": "gwbzsussxu5",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": Close
  }
}

    FASTERLONG = {
  "name": "FASTER LONG",
  "secret": "xxuxkqf0gpj",
  "side": "buy",
  "symbol": symbol,
  "open": {
    "price": Close
  }
}  


    FASTERSHORT = {
  "name": "FASTER SHORT",
  "secret": "w48ulz23f6",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": Close
  }
}


# Noro strategy:
  if (Close < long[-2]) and (rsi[-2] > 20) and (Close < middleband[-2]):
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n📍 Picker: {round(long[-2],4)} Low: {low_price}") 
      requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=PICKERLONG)
   
  if (Close > short[-2]) and (rsi[-2] < 80) and (Close > middleband[-2]):
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n📍 Picker: {round(short[-2],4)} High: {high_price}")
      requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=PICKERSHORT)
      requests.post('https://hook.finandy.com/DRt05cAn8UjMWv5bqVUK', json=CARLOSSHORT) 
      
# Tendencia
  if cciB[-3] > cciB[-2] :
    if (df['ema_200'][-3] < df['ema_13'][-3]) and (df['ema_200'][-2] > df['ema_13'][-2]) and (cci_20[-3] > cci_20[-2]) and (cci_20[-2] < 50):      
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n🏄🏻 KROSS")
      requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=FASTERSHORT)
  if cciB[-3] < cciB[-2] :    
    if (df['ema_200'][-3] > df['ema_13'][-3]) and (df['ema_200'][-2] < df['ema_13'][-2]) and (cci_20[-3] < cci_20[-2] > 100) and (cci_20[-2] > -50): 
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n🏄‍♂️ KROSS") 
      requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=FASTERLONG)
         
# Contra tendencia al 1%   
  if (Close <= upperband[-2]) and (cci_20[-2] >= 250): 
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n📍 1%") 
      requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT)
         
  if (Close >= lowerband[-2]) and (cci_20[-2] <= -250):
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n📍 1%")
      requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG)
               
while True:
  current_time = ti.time()
  seconds_to_wait = 180 - current_time % 180
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      print(symbol)
