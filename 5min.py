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
        df['ema_cross'] = np.where(df['EMA13'] > df['EMA100'], np.where(df['EMA13'][-1] <= df['EMA100'][-1],1,0), np.where(df['EMA13'][-1] >= df['EMA100'][-1], -1, 0))
        df['Volume_prom'] = df['Close'].mean()
        df['diff'] = abs((df['High'] / df['Low'] -1) * 100) 
        
        def get_accumulation_points(client, symbol, num_periods=10):
          klines = client.futures_klines(symbol=symbol, interval='1h', limit=num_periods)
          prices = [float(kline[1]) for kline in klines]
          volumes = [float(kline[5]) for kline in klines]
          bid_accumulation_points = []
          ask_accumulation_points = []
          for i in range(num_periods):
            depth = client.futures_order_book(symbol=symbol, limit=5)
            bid_accumulation_points.append(sum(float(bid[1]) for bid in depth['bids']))
            ask_accumulation_points.append(sum(float(ask[1]) for ask in depth['asks']))
            nearest_bid_price = prices[bid_accumulation_points.index(max(bid_accumulation_points))]
            nearest_ask_price = prices[ask_accumulation_points.index(max(ask_accumulation_points))]
          return nearest_bid_price, nearest_ask_price
        
        nearest_bid_price, nearest_ask_price = get_accumulation_points(client, symbol, num_periods=10)
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
        "price": nearest_ask_price
        }
        }
        
        BOUNCYLONG = {
        "name": "BOUNCY LONG",
        "secret": "xjth0i3qgb",
        "side": "buy",
        "symbol": symbol,
         "open": {
        "price": nearest_bid_price
        }
        }  
    
        CONTRASHORT = {
        "name": "CONTRA SHORT",
        "secret": "w48ulz23f6",
        "side": "sell",
        "symbol": symbol,
        "open": {
        "price": nearest_ask_price
        }
        }
        CONTRALONG = {
        "name": "CONTRA LONG",
        "secret": "xxuxkqf0gpj",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": nearest_bid_price
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
              
        # Calcular los niveles Fibonacci
        precio_high = max(df['Close'])
        precio_low = min(df['Close'])
        diff_precio = precio_high - precio_low
        nivel_786 = precio_high - (0.786)*(diff_precio)
        nivel_382 = precio_high - (0.382)*(diff_precio)
        
        depth = 5

        response = requests.get(f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit={depth}').json()

        if 'bids' in response:
          bid_sum = sum([float(bid[1]) for bid in response['bids']])
        else:
          bid_sum = 0.0

        if 'asks' in response:
          ask_sum = sum([float(ask[1]) for ask in response['asks']])
        else:
          ask_sum = 0.0

        if bid_sum + ask_sum > 0:
          imbalance = (ask_sum - bid_sum) / (bid_sum + ask_sum)
        else:
          imbalance = 0.0 
                                                    
        # TENDENCIA ALCISTA:
        if (df['diff'][-2] > 1) and (float(df['Close'][-2]) > upperband[-2]) and (rsi[-2] >= 50) and (adx[-2] <= 20):
          Tb.telegram_send_message(f"🎣 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\n⛳️ Snipper : {nearest_bid_price} \nIMB : {round(imbalance,2)} \n(🎣 Fishing Pisha")
          requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
        elif (df['diff'][-2] > 1) and (float(df['Close'][-2]) > upperband[-2]) and (rsi[-2] >= 75) and (adx[-2] >= 40): 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Cambio: % {round(df['diff'][-3],2)} \n💵 Precio: {float(df['Close'][-2])}\nIMB : {round(imbalance,2)} \n⛳️ Snipper : {nearest_ask_price} ")
          requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=CONTRASHORT)   
        
        # TENDENCIA BAJISTA:
        if (df['diff'][-2] > 1) and (float(df['Close'][-2]) < lowerband[-2]) and (rsi[-2] <= 50) and (adx[-2] <= 20):
          Tb.telegram_send_message(f"🎣 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\n⛳️ Snipper : {nearest_ask_price}\nIMB : {round(imbalance,2)} \n🎣 Fishing Pisha")
          requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT)
        elif (df['diff'][-2] > 1) and (float(df['Close'][-2]) < lowerband[-2]) and (rsi[-2] <= 25) and (adx[-2] <= 20): 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Cambio: % {round(df['diff'][-3],2)} \n💵 Precio: {float(df['Close'][-2])}\nIMB : {round(imbalance,2)} \n⛳️ Snipper : {nearest_bid_price} ")
          requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=CONTRALONG)   
        
        # Tendencia:
        
        if (df['EMA200'][-2] > float(df['Close'][-2])) and (df['EMA13'][-3] < float(df['Close'][-3])) and (df['EMA13'][-2] > float(df['Close'][-2])) and (40 > rsi[-2] >= 30):
            Tb.telegram_send_message(f"🦘 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\n⛳️ Snipper : {nearest_ask_price}\nIMB : {round(imbalance,2)} \n🦘 Bouncy")
            requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=BOUNCYSHORT)   
        
        if (df['EMA200'][-2] < float(df['Close'][-2])) and (df['EMA13'][-3] > float(df['Close'][-3])) and (df['EMA13'][-2] < float(df['Close'][-2])) and (70 > rsi[-2] >= 60): 
            Tb.telegram_send_message(f"🦘 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\n⛳️ Snipper : {nearest_bid_price}\nIMB : {round(imbalance,2)} \n🦘 Bouncy")
            requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=BOUNCYLONG) 
        
        #Cruce de EMAS + FIBO:
       
        if (df['ema_cross'][-1] == 1 and (float(df['Close'][-1] > nivel_786))) or (df['ema_cross'][-1] == 1 and (float(df['Close'][-1] > nivel_382))):
            Tb.telegram_canal_prueba(f"🐬 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\n⛳️ Snipper : {nearest_bid_price}\nIMB : {round(imbalance,2)} \n🐬 Delfin")  
            requests.post('https://hook.finandy.com/9nQNB3NdMGaoK-xWqVUK', json=DELFINLONG) 
        
        if (df['ema_cross'][-1] == -1 and (float(df['Close'][-1] < nivel_786))) or (df['ema_cross'][-1] == 1 and (float(df['Close'][-1] < nivel_382))):
            Tb.telegram_canal_prueba(f"🐬 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {float(df['Close'][-2])}\n⛳️ Snipper : {nearest_ask_price}\nIMB : {round(imbalance,2)} \n🐬 Delfin")
                  
while True:
  # Espera hasta que sea el comienzo de una nueva hora
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
    indicator(symbol)
    print(symbol)
