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
  
  kline = client.futures_historical_klines(symbol, "3m", "12 hours ago UTC+1",limit=500)
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
    cci20 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)
    
    upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
    depth = 5
    order_book = client.futures_order_book(symbol=symbol, limit=depth)

    bid_sum = sum([float(bid[1]) for bid in order_book['bids']])
    ask_sum = sum([float(ask[1]) for ask in order_book['asks']])
    max_bid = float(order_book['bids'][0][0])
    max_ask = float(order_book['asks'][0][0])
    mean_price = (max_ask + max_bid )/2
    spread = max_ask - max_bid  # Calcula el spread
    spread_por = ((max_ask - max_bid ) /mean_price)*100
 
    if bid_sum + ask_sum > 0:
     imbalance = (ask_sum - bid_sum) / (bid_sum + ask_sum)
    else:
     imbalance = 0.0
    
    
    PORSHORT = {
    "name": "CORTO 3POR",
    "secret": "ao2cgree8fp",
    "side": "sell",
    "symbol": symbol,
    "open": {
    "price": max_ask
    }
    }
    PORLONG = {
    "name": "LARGO 3POR",
    "secret": "nwh2tbpay1r",
    "side": "buy",
    "symbol": symbol,
    "open": {
    "price": max_bid
    }
    }
    
    BOUNCYSHORT= {
  "name": "BOUNCY SHORT",
  "secret": "hgw3399vhh",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": max_ask
  }
}
    BOUNCYLONG= {
  "name": "BOUNCY LONG",
  "secret": "xjth0i3qgb",
  "side": "buy",
  "symbol": symbol,
  "open": {
    "price": max_bid
  }
}
      # Chequea si el precio es mayor al canal más alto de Fibonacci y si hay un cruce bajista de MACD y Signal o un cruce bajista del RSI y el nivel 70
    
      #Actual   
    if (rsi[-2] >= 70) and (imbalance < -0.65) and (spread_por < 0.005):
        Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n IMB: {round(imbalance,2)}") 
        requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT) 
    if (rsi[-2] <= 30) and (imbalance > 0.65) and (spread_por > 0.005):
        Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}\n IMB: {round(imbalance,2)}")
        requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG) 
    if (cci20[-2] < -100) and (imbalance < -0.0) and (spread_por < 0.005):
        Tb.telegram_canal_prueba(f"C-I {symbol}\n🔴 SHORT\n⏳ 3 min\n💵 Precio: {Close}\nIMB : {round(imbalance,2)} C-I bid {max_bid} ask {max_ask}  " ) 
        requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=BOUNCYSHORT)     
    if (cci20[-2] > 100) and (imbalance > 0.70) and (spread_por > 0.005):
        Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min\n💵 Precio: {Close}\nIMB : {round(imbalance,2)} C-I bid {max_bid} ask {max_ask}  ")
        requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=BOUNCYLONG) 
               
while True:
  current_time = ti.time()
  seconds_to_wait = 180 - current_time % 180
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      print(symbol)
