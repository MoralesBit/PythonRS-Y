from binance.client import Client
import pandas as pd
import numpy as np
import talib as ta
import Telegram_bot as Tb
import  schedule as schedule
import time as ti
import requests
import json

api_key = 'TU_API_KEY'
api_secret = 'TU_API_SECRET'

client = Client(api_key, api_secret)

futures_info = client.futures_exchange_info()
symbols = [
    symbol['symbol'] for symbol in futures_info['symbols']
    if symbol['status'] == "TRADING"
  ] 

def indicator(symbol):   
        kline = client.futures_historical_klines(symbol, "5m", "2 days ago UTC+1",limit=500)
        df = pd.read_json(json.dumps(kline))
    
        if not df.empty:
          df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close' 'IGNORE',
        'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
        df['Date'] = pd.to_datetime(df['Date'], unit='ms')
        df = df.set_index('Date')
      
    
        upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                                timeperiod=20,
                                                nbdevup=2,
                                                nbdevdn=2,
                                                matype=0)
        df['upperband'] = upperband
        df['middleband'] = middleband
        df['lowerband'] = lowerband
          
        rsi = ta.RSI(df["Close"], timeperiod=14)
        adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
                         
        df['EMA13'] = df['Close'].ewm(13).mean()
        df['EMA200'] = df['Close'].ewm(200).mean()
        df['EMA100'] = df['Close'].ewm(100).mean()
        df['Volume_prom'] = df['Close'].mean()

        df['diff'] = abs((df['High'] / df['Low'] -1) * 100) 
            
        klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE)
        prices = np.array([float(kline[2]) for kline in klines])
        prices_high = np.array([float(kline[3]) for kline in klines])
        prices_low = np.array([float(kline[4]) for kline in klines])
        
        cciBTC = ta.CCI(prices_high, prices_low, prices, timeperiod=20)
      
        def get_max_bid_ask(client, symbol):
          depth = client.futures_order_book(symbol=symbol, limit=50)
          bids = depth['bids']
          asks = depth['asks']
          max_bids = sorted([float(bid[0]) for bid in bids], reverse=True)[:5]
          max_asks = sorted([float(ask[0]) for ask in asks])[:5]
          return max_bids, max_asks                
        
                
        # DATOS FNDY
        FISHINGSHORT = {
        "name": "FISHING SHORT",
        "secret": "azsdb9x719",
        "side": "sell",
        "symbol": symbol,
        "open": {
        "price": float(df['Close'][-2])
        }
        }
        
        FISHINGLONG = {
        "name": "FISHING LONG",
        "secret": "0kivpja7tz89",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": float(df['Close'][-2])
        }
        }
    
        BOUNCYSHORT = {
        "name": "BOUNCY SHORT",
        "secret": "hgw3399vhh",
        "side": "sell",
        "symbol": symbol,
         "open": {
        "price": float(df['Close'][-2])
        }
        }
        
        BOUNCYLONG = {
        "name": "BOUNCY LONG",
        "secret": "xjth0i3qgb",
        "side": "buy",
        "symbol": symbol,
         "open": {
        "price": float(df['Close'][-2])
        }
        }  
    
        CONTRASHORT = {
        "name": "CONTRA SHORT",
        "secret": "w48ulz23f6",
        "side": "sell",
        "symbol": symbol,
        "open": {
        "price": float(df['Close'][-2])
        }
        }
        CONTRALONG = {
        "name": "CONTRA LONG",
        "secret": "xxuxkqf0gpj",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": float(df['Close'][-2])
        }
        }
        
        DELFINLONG = {
        "name": "DELFIN LONG",
        "secret": "an0rvlxehbn",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": float(df['Close'][-2])
        }
        }
        
        max_bids, max_asks = get_max_bid_ask(client, symbol)
            
             
        # TENDENCIA ALCISTA:
        if (df['diff'][-3] > 1) and (df['diff'][-2] < 2) and (float(df['Close'][-3]) > upperband[-3]) and (rsi[-3] >= 70) and  (df['Volume'][-2] >= df['Volume_prom'][-2]) and (float(df['Close'][-2]) > float(df['Open'][-2])) and (adx[-2] < 25):
          Tb.telegram_send_message(f"🎣 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\n⛳️ Snipper : {max_bids[-3]} \n🎣 Fishing Pisha")
          requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
        elif (df['diff'][-3] > 1) and (df['diff'][-2] < 2) and (float(df['Close'][-3]) > upperband[-3]) and (rsi[-3] > 80) and  (df['Volume'][-2] >= df['Volume_prom'][-2]) and (float(df['Close'][-2]) < float(df['Open'][-2])) and (adx[-2] > 30): 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Cambio: % {round(df['diff'][-3],2)} \n💵 Precio: {float(df['Close'][-2])} \n⛳️ Snipper : {max_asks[-3]} ")
          requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CONTRASHORT)   
        
        # TENDENCIA BAJISTA:
        if (df['diff'][-3] > 1) and (df['diff'][-2] < 2) and (float(df['Close'][-3]) < lowerband[-3]) and (rsi[-3] <= 30) and (df['Volume'][-2] >= df['Volume_prom'][-2]) and (float(df['Close'][-2]) < float(df['Open'][-2])) and (adx[-2] < 25):
          Tb.telegram_send_message(f"🎣 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\n⛳️ Snipper : {max_asks[-3]} \n🎣 Fishing Pisha")
          requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT)
        elif (df['diff'][-3] > 1) and (df['diff'][-2] < 2) and (float(df['Close'][-3]) < lowerband[-3]) and (rsi[-3] < 20) and (df['Volume'][-2] >= df['Volume_prom'][-2]) and (float(df['Close'][-2]) > float(df['Open'][-2])) and (adx[-2] > 30): 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Cambio: % {round(df['diff'][-3],2)} \n💵 Precio: {float(df['Close'][-2])} \n⛳️ Snipper : {max_bids[-3]} ")
          requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=CONTRALONG)   
        
        # Tendencia:
        if cciBTC[-2] > 50 :
          if (df['EMA200'][-2] > float(df['Close'][-2])) and (df['EMA13'][-3] < float(df['Close'][-3])) and (df['EMA13'][-2] > float(df['Close'][-2])) and (40 > rsi[-2] >= 30):
            Tb.telegram_send_message(f"🦘 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\n⛳️ Snipper : {max_asks[-3]} \n🦘 Bouncy")
            requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=BOUNCYSHORT)   
        if cciBTC[-2] < -50 :
          if (df['EMA200'][-2] < float(df['Close'][-2])) and (df['EMA13'][-3] > float(df['Close'][-3])) and (df['EMA13'][-2] < float(df['Close'][-2])) and (70 > rsi[-2] >= 60): 
            Tb.telegram_send_message(f"🦘 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\n⛳️ Snipper : {max_bids[-3]} \n🦘 Bouncy")
            requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=BOUNCYLONG) 
        
        # CCI FOREX::
        #if cciBTC[-2] > 0 :
          #if (cci20[-3] < 0) and (cci20[-2] > 0) and (adx[-2] > 25):
            #Tb.telegram_canal_prueba(f"🐬 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {Close}\n⛳️ Snipper : {max_bid} \n🐬 Delfin")  
            #requests.post('https://hook.finandy.com/9nQNB3NdMGaoK-xWqVUK', json=DELFINLONG) 
                  
while True:
  # Espera hasta que sea el comienzo de una nueva hora
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
    indicator(symbol)
    print(symbol)
