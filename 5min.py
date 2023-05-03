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
  
  kline = client.futures_historical_klines(symbol, "5m", "24 hours ago UTC+1",limit=1000)
  df = pd.DataFrame(kline)
  
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
    
    #Calculo RSI:
    rsi = ta.RSI(df["Close"], timeperiod=14)
    
    #Calculo ADX
    adx= ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
    
    # Calculo de DIFF:
    Close = float(df['Close'][-2])
    Close_3 = float(df['Close'][-3])
    High = float(df['High'][-2])
    Low = float(df['Low'][-2])
    Open = float(df['Open'][-2])
    diff = abs((High / Low -1) * 100)
#   diff_high = abs((High / Close -1)*100)
#   diff_low = abs((Low / Close -1)*100)

    df['STD_5'] = ta.STDDEV(df['Close'], timeperiod=5, nbdev=1)
    df['STD_5_promedio'] = df['STD_5'].mean()

    #Calculo de EMAS:
    df['ema_13'] = df['Close'].ewm(span=13, adjust=False).mean()
    df['ema_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['ema_660'] = df['Close'].ewm(span=660, adjust=False).mean()
    
    # Calclulo CCI:
    cci_20 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)
    
    #Calculo ESTOCASTICO:
#   slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)

    #Calculo ROC
    roc = ta.ROC(df['Close'], timeperiod=10) 
    
    # Calculo Bollinger:
    upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
       
    #noro strategy
    var = 0.65
    ma = ta.SMA(df['Close'], timeperiod=3)
    long = ma + ((ma / 100) *(-var))
    short = ma + ((ma / 100) *(var))
       
    
    # Entradas en cola:
    enter_high = (Close + High)/2
    enter_low = (Close + Low)/2
    
    
          
    PORSHORT = {
    "name": "CORTO 3POR",
    "secret": "ao2cgree8fp",
    "side": "sell",
    "symbol": symbol,
    "open": {
    "price": enter_high
    }
    }
    PORLONG = {
    "name": "LARGO 3POR",
    "secret": "nwh2tbpay1r",
    "side": "buy",
    "symbol": symbol,
    "open": {
    "price": enter_low
    }
    }
    
    PICKERSHORT= {
  "name": "PICKER SHORT",
  "secret": "hgw3399vhh",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": enter_high
  }
}
    PICKERLONG = {
  "name": "PICKER LONG",
  "secret": "xjth0i3qgb",
  "side": "buy",
  "symbol": symbol,
  "open": {
    "price": enter_low
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
  # DATOS FNDY
  FISHINGSHORT = {
        "name": "FISHING SHORT",
        "secret": "azsdb9x719",
        "side": "sell",
        "symbol": symbol,
        "open": {
        "price": Close
        }
        }
        
  FISHINGLONG = {
        "name": "FISHING LONG",
        "secret": "0kivpja7tz89",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": Close
        }
        }    
   
   
# KC strategy:
  if (Close > df['ema_660'][-2]):
    if (Close < long[-2]):
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n📍 Picker: {round(enter_low,6)}") 
      requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=PICKERLONG)
      
  if (Close < df['ema_660'][-2]):
   if (Close > short[-2]):
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n📍 Picker: {round(enter_high,6)}")
      requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=PICKERSHORT)
      requests.post('https://hook.finandy.com/DRt05cAn8UjMWv5bqVUK', json=CARLOSSHORT) 
      
# Tendencia:
#  if (df['ema_13'][-2] < df['ema_660'][-2]) and (adx[-2] >= 20):
#    if (df['ema_50'][-3] < df['ema_13'][-3]) and (df['ema_50'][-2] > df['ema_13'][-2]) and (cci_20[-3] > cci_20[-2]):      
#      Tb.telegram_send_message(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n💵 Precio: {Close}\n🎣 Fishing Pisha")
#      requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT) 
  
#  if (df['ema_13'][-2] > df['ema_660'][-2]) and (adx[-2] >= 20):    
#    if (df['ema_50'][-3] > df['ema_13'][-3]) and (df['ema_50'][-2] < df['ema_13'][-2]) and (cci_20[-3] < cci_20[-2]): 
#      Tb.telegram_send_message(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n💵 Precio: {Close}\n🎣 Fishing Pisha") 
#      requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG)
         
# Contra tendencia al 1%   
  if (roc[-2] >= 1) and (Close >= upperband[-2]) and (rsi[-2] >= 70) and (df['STD_5'][-2] > df['STD_5_promedio'][-2]):  
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n📍 Enter: {round(enter_high,6)}") 
      requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT)
         
  if (roc[-2] <= -1) and (Close <= lowerband[-2]) and (rsi[-2] <= 30) and (df['STD_5'][-2] > df['STD_5_promedio'][-2]):
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n📍 Enter: {round(enter_low,6)}")
      requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG)
               
while True:
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      print(symbol)
