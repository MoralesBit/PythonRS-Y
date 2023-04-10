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
        kline = client.futures_historical_klines(symbol, "5m", "12 hours ago UTC+1",limit=500)
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
    
        macd, signal, hist = ta.MACD(df['Close'], 
                                      fastperiod=12, 
                                      slowperiod=26, 
                                      signalperiod=9)
        df['macd'] = macd
        df['macd_signal'] = signal
        df['macd_hist'] = hist
        df['macd_crossover'] = np.where(df['macd'] > df['macd_signal'], 1, 0)
        df['position_macd'] = df['macd_crossover'].diff()
    
        rsi = ta.RSI(df["Close"], timeperiod=14)
        adx = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
        slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        df['Will'] = ta.WILLR(df['High'], df['Low'], df['Close'], timeperiod=14)
        df['BBW'] = (df['upperband'] - df['lowerband']) / df['middleband']  
        chain = ta.ADOSC(df['High'], df['Low'], df['Close'], df['Volume'], fastperiod=3, slowperiod=10)
        cci20 = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=20)
        
        df['EMA200'] = df['Close'].ewm(200).mean()
        df['EMA100'] = df['Close'].ewm(100).mean()
    
        df['tendencia'] = np.where((float(df['Close'][-2])) > (df['EMA100'][-2]),1,0)
        df['tendenciaemas'] = np.where(df['EMA100'][-2] > (df['EMA200'][-2]),1,0)
    
        df['max_price'] = (df['Close']).max()
        df['min_price'] = (df['Close']).min()
      
      
        df['diference'] = df['max_price'] - df['min_price']
      
        df['cero_level'] = df['max_price'] -  df['diference']*0
        df['first_level'] = df['max_price'] -  df['diference']*0.236
        df['secound_level'] = df['max_price'] -  df['diference']* 0.382
        df['third_level'] = df['max_price'] -  df['diference']*0.5
        df['fourth_level'] = df['max_price'] -  df['diference']*0.618
        df['uno_level'] = df['max_price'] -  df['diference']*1
    
        df['cero_cross'] = np.where((float(df['Close'][-2])) > (df['cero_level']),1,0)
        df['first_cross'] = np.where((float(df['Close'][-2])) > (df['first_level']),1,0)
        df['secound_cross'] = np.where((float(df['Close'][-2])) > (df['secound_level']),1,0)
        df['third_cross'] = np.where((float(df['Close'][-2])) > (df['third_level']),1,0)
        df['fourth_cross'] = np.where((float(df['Close'][-2])) > (df['fourth_level']),1,0)
        df['uno_cross'] = np.where((float(df['Close'][-2])) > (df['uno_level']),1,0)
    
        Close = float(df['Close'][-2])
        Close3 = float(df['Close'][-3])
        Open = float(df['Open'][-2])
        High = float(df['High'][-2])
        Low = float(df['Low'][-2])
        diff = abs((High / Low -1) * 100)  

        depth = client.futures_order_book(symbol=symbol, limit=50)
        bids = depth['bids']
        asks = depth['asks']
        max_bid = max([float(bid[0]) for bid in bids[-10:]])
        max_ask = max([float(ask[0]) for ask in asks[-10:]])
    
        # Calculate Fibonacci
        #basis = ta.WMA(df['Close'], timeperiod=20)
        #dev = (3) * ta.STDDEV(df['Close'], timeperiod=20)
        #fu764 = basis + (0.001 * 764 * dev)
        #fu5 = basis + (0.001 * 500 * dev)
        #fu1 = basis + (1 * dev)      
        #fd764 = basis - (0.001 * 764 * dev)
         #fd5 = basis - (0.001 * 500 * dev)
        #fd1 = basis - (1 * dev)
    
        # DATOS FNDY
        FISHINGSHORT = {
        "name": "FISHING SHORT",
        "secret": "azsdb9x719",
        "side": "sell",
        "symbol": symbol,
        "open": {
        "price": max_ask
        }
        }
        
        FISHINGLONG = {
        "name": "FISHING LONG",
        "secret": "0kivpja7tz89",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": max_bid
        }
        }
    
        CONTRASHORT = {
        "name": "SHORT-MINIFISH",
        "secret": "hgw3399vhh",
        "side": "sell",
        "symbol": symbol
        }
        CONTRALONG = {
        "name": "LONG-MINIFISH",
        "secret": "xjth0i3qgb",
        "side": "buy",
        "symbol": symbol
        }  
    
        VIEWSHORT = {
        "name": "VIEW SHOR",
        "secret": "w48ulz23f6",
        "side": "sell",
        "symbol": symbol
        }
        VIEWLONG = {
        "name": "VIEW LONG",
        "secret": "xxuxkqf0gpj",
        "side": "buy",
        "symbol": symbol
        }
     
       

        # Contra-Tendencia (Cierre de la tendencia)
        if (rsi[-3] > 70) and (slowk[-3] > slowk[-2]) and (Close > max_ask) :
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {Close}\n📈 RSI : {round(rsi[-2],3)}\n")
          requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=CONTRASHORT)   
        if (rsi[-3] < 30) and (slowk[-3] < slowk[-2]) and (Close < max_bid) : 
          Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {Close}\n📉 RSI : {round(rsi[-2],3)}\n")
          requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=CONTRALONG) 
        
      #Tendencia FISHING
        if (df['EMA200'][-2] > Close) and (float(df['Close'][-2]) < float(df['fourth_level'][-2])) and (float(df['fourth_level'][-3])) < (float(df['Close'][-3])) and (adx[-2] > 40):
          Tb.telegram_send_message(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {Close}\n⛳️ Snipper : {max_ask} \n🎣 Fishing Pisha") 
          requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT) 
        if (df['EMA200'][-2] < Close ) and (float(df['Close'][-2]) > float(df['fourth_level'][-2])) and (float(df['fourth_level'][-3])) > (float(df['Close'][-3])) and (adx[-2] < 20):
          Tb.telegram_send_message(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {Close}\n⛳️ Snipper : {max_bid} \n🎣 Fishing Pisha") 
          requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
        
        #Tendencia view
        if (df['EMA200'][-2] > Close) and (float(df['Close'][-2]) < max_ask) and (max_ask) < (float(df['Close'][-3])) and (adx[-2] > 40):
         Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {Close}\n TW") 
         requests.post('https://hook.finandy.com/gZZtqWYCtUdF0WwyqFUK', json=VIEWSHORT) 
        if (df['EMA200'][-2] < Close ) and (float(df['Close'][-2]) > max_bid) and max_bid > (float(df['Close'][-3])) and (adx[-2] < 20):
          Tb.telegram_canal_prueba(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {Close}\n TW") 
          requests.post('https://hook.finandy.com/VMfD-y_3G5EgI5DUqFUK', json=VIEWLONG)
          
           
while True:
  # Espera hasta que sea el comienzo de una nueva hora
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
    indicator(symbol)
    print(symbol) 
