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
    cci20 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)
    ema_200 = df['Close'].ewm(span=200, adjust=False).mean()
    adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
    
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
     
    info = client.futures_historical_klines("BTCUSDT", "15m", "2 days ago UTC+1",limit=1000) 
    df_new = pd.DataFrame(info)
       
    if not df_new.empty:
        df_new.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close' 'IGNORE',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df_new['Date'] = pd.to_datetime(df_new['Date'], unit='ms')
    df_new = df_new.set_index('Date')
    cciB = ta.CCI(df_new['High'], df_new['Low'], df_new['Close'], timeperiod=20)
    
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
    
    TRENDSHORT= {
  "name": "TREND SHORT",
  "secret": "hgw3399vhh",
  "side": "sell",
  "symbol": symbol,
  "open": {
    "price": Close
  }
}
    TRENDLONG= {
  "name": "TREND LONG",
  "secret": "xjth0i3qgb",
  "side": "buy",
  "symbol": symbol,
  "open": {
    "price": Close
  }
}
   
    #Contra tendencia al 1%   
    if (rsi[-2] >= 80) and (diff > 1) and (ask_sum > bid_sum) and (adx[-2] >= 30):
        Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}") 
        requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT) 
    if (rsi[-2] <= 20) and (diff > 1) and (ask_sum < bid_sum) and (adx[-2] <= 30):
        Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(diff,2)} \n💵 Precio: {Close}")
        requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG) 
        
    #Tendencia:     
    if (cciB[-2] < 0) and (imbalance < -0.50):
      if (60 < rsi[-2] < 70) or (40 < rsi[-2] < 50):
        Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min\n💵 Precio: {Close} \n⛳️ Trend" ) 
        requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=TRENDSHORT)     
    if (cciB[-2] > 0) and (imbalance > 0.50): 
      if (30 < rsi[-2] < 40) or (50 < rsi[-2] < 60):
        Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min\n💵 Precio: {Close} \n⛳️ Trend")
        requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=TRENDLONG) 
               
while True:
  current_time = ti.time()
  seconds_to_wait = 180 - current_time % 180
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      print(symbol)
