from binance.client import Client
import pandas as pd
import talib as ta
import Telegram_bot as Tb
import  schedule as schedule
import time as ti
import requests

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
    High = float(df['High'][-2])
    Low = float(df['Low'][-2])
    diff = abs((High / Low -1) * 100)
    #cci20 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)
    #ema_200 = df['Close'].ewm(span=200, adjust=False).mean()
    #adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
    ad = ta.AD(df['High'], df['Low'], df['Close'], df['Volume'])
    df['Close'] = df['Close'].astype(float)
    delta = df['Close'].diff()
    fi = delta * ad
    #macd, signal, hist = ta.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
   
    
    
    upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
    #depth = 5
    #order_book = client.futures_order_book(symbol=symbol, limit=depth)

    #bid_sum = sum([float(bid[1]) for bid in order_book['bids']])
    #ask_sum = sum([float(ask[1]) for ask in order_book['asks']])
    #max_bid = float(order_book['bids'][0][0])
    #max_ask = float(order_book['asks'][0][0])
 
    #if bid_sum + ask_sum > 0:
     #imbalanceS = (ask_sum - bid_sum) / (bid_sum + ask_sum)
    #else:
     #imbalanceS = 0.0
    
    #depth = 5
    #order_book = client.futures_order_book(symbol=symbol, limit=depth)

    #bid_sum = sum([float(bid[1]) for bid in order_book['bids']])
    #ask_sum = sum([float(ask[1]) for ask in order_book['asks']])
    #max_bid = float(order_book['bids'][0][0])
    #max_ask = float(order_book['asks'][0][0])
    #mean_price = (max_ask + max_bid )/2
    #spread = max_ask - max_bid  # Calcula el spread
    #spread_por = ((max_ask - max_bid ) /mean_price)*100
 
    #if bid_sum + ask_sum > 0:
    # imbalance = (ask_sum - bid_sum) / (bid_sum + ask_sum)
    #else:
    # imbalance = 0.0
    
    #noro strategy
    ma = ta.SMA(df['Close'], timeperiod=3)
    long = ma + ((ma / 100) *(-1))
    short = ma + ((ma / 100) *(1))
       
    # Enviar la solicitud a la API pública de Binance
    response = requests.get(f'https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}')

# Obtener el volumen de negociación de las últimas 24 horas
    volume = float(response.json()['volume'])
    
    depth = 5
    order_book = client.futures_order_book(symbol=symbol, limit=depth)

    bid_sum = sum([float(bid[1]) for bid in order_book['bids']])
    ask_sum = sum([float(ask[1]) for ask in order_book['asks']])
    max_bid = float(order_book['bids'][0][0])
    max_ask = float(order_book['asks'][0][0])
 
    if bid_sum + ask_sum > 0:
     imbalance = (ask_sum - bid_sum) / (bid_sum + ask_sum)
    else:
     imbalance = 0.0
    
    enter = Close*(0.97)
    
    
    PORSHORT = {
    "name": "CORTO 3POR",
    "secret": "ao2cgree8fp",
    "side": "sell",
    "symbol": symbol,
    "open": {
    "price": enter
    }
    }
    PORLONG = {
    "name": "LARGO 3POR",
    "secret": "nwh2tbpay1r",
    "side": "buy",
    "symbol": symbol,
    "open": {
    "price": enter
    }
    }
    
    PICKERSHORT= {
  "name": "PICKER SHORT",
  "secret": "hgw3399vhh",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": enter
  }
}
    PICKERLONG = {
  "name": "PICKER LONG",
  "secret": "xjth0i3qgb",
  "side": "buy",
  "symbol": symbol,
  "open": {
    "price": enter
  }
}
  CARLOSSHORT = {
  "name": "Hook 200276",
  "secret": "gwbzsussxu5",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": enter
  }
}

  FASTERLONG = {
  "name": "FASTER LONG",
  "secret": "xxuxkqf0gpj",
  "side": "buy",
  "symbol": symbol,
  "open": {
    "price": enter
  }
}  


  FASTERSHORT = {
  "name": "FASTER SHORT",
  "secret": "w48ulz23f6",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": enter
  }
}
      
    #Noro strategy:
  if (Close <= long[-2]) and (rsi[-2] > 20):
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n📍 Picker: {round(imbalance,2)}") 
      requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=PICKERLONG)
  if (Close >= short[-2]) and (rsi[-2] > 80):  
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n🏄‍♂️ FASTER: {round(imbalance,2)}") 
      requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=FASTERLONG)
  
  if ((Close >= short[-2]) and (rsi[-2] < 80)):
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n📍 Picker: {round(imbalance,2)}")
      requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=PICKERSHORT)
      requests.post('https://hook.finandy.com/DRt05cAn8UjMWv5bqVUK', json=CARLOSSHORT) 
  if  (Close <= long[-2]) and (rsi[-2] < 20):      
      Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n🏄🏻 FASTER: {round(imbalance,2)}")
      requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=FASTERSHORT)
      
    #Contra tendencia al 1%   
  if (diff > 1) and (Close < lowerband[-2]) and (rsi[-2] > 70) (slowk[-2] > slowd[-2] >= 80):
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}") 
      requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT)
         
  if (diff > 1) and (Close > upperband[-2]) and (rsi[-2] < 30) and (slowk[-2] < slowd[-2] <= 20):
      Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}")
      requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG)
               
while True:
  current_time = ti.time()
  seconds_to_wait = 180 - current_time % 180
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      print(symbol)
