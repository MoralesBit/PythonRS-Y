import time
import requests
import numpy as np
import pandas as pd
import talib as ta
from binance.client import Client
import Telegram_bot as Tb

Pkey = ''
Skey = ''
client = Client(api_key=Pkey, api_secret=Skey)

def get_trading_symbols():
    """Obtiene la lista de símbolos de futuros de Binance que están disponibles para trading"""
    futures_info = client.futures_exchange_info()
    symbols = [symbol['symbol'] for symbol in futures_info['symbols'] if symbol['status'] == "TRADING"]
      
    return symbols

   
def calculate_indicators(symbol):
    """Calcula los indicadores de Bollinger para un símbolo y devuelve las últimas velas"""
    klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE, limit=1000)
    df = pd.DataFrame(klines)
    if df.empty:
        return None
    df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                  'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    df = df.set_index('Open time')
    
    upperband, middleband, lowerband = ta.BBANDS(df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['upperband'] = upperband
    df['middleband'] = middleband
    df['lowerband'] = lowerband
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
    df['BB'] = (df['Close'] - df['lowerband']) / (df['upperband'] - df['lowerband'])
    df['diff'] = abs((df['High'] / df['Low'] - 1) * 100)
    rsi = ta.RSI(df['Close'], timeperiod=14)
    df['rsi'] = rsi 
    adx= ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
    df['adx'] = adx
    ema_50 = df['Close'].ewm(span=50, adjust=False).mean()
    df['ema_50'] = ema_50
    roc = ta.ROC(df['Close'], timeperiod=6)
    df['roc'] = roc
    
     
    
    return df[-3:]
  
def get_last_funding_rate(symbol):
  # Obtener el historial de tasas de financiamiento
    funding_history = client.futures_funding_rate(symbol=symbol)

    # Imprimir las tasas de financiamiento
    for funding_info in funding_history:
      ff = float(funding_info['fundingRate'])*100
      
    return ff
    
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
        ff = get_last_funding_rate(symbol)
        print(symbol)
        print(ff)
                       
        try:
            df = calculate_indicators(symbol)
            
            if df is None:
                continue
            # CONTRATENDENCIAs:         
            
            if (df['rsi'][-2] > 70) and (df['roc'][-2] > 3):     
                    
             if (df['rsi'][-3] < df['rsi'][-2] > df['rsi'][-1]): 
 
              Tb.telegram_canal_3por(f"🔴 {symbol}\n🔝 Cambio: % {round(df['roc'][-2],2)} \n💵 Precio: {df['Close'][-2]}\n📍 Picker ▫️ 5 min")
            
              PICKERSHORT= {
                "name": "PICKER SHORT",
                "secret": "hgw3399vhh",
                "side": "sell",
                "symbol": symbol,
                "open": {
                "price": float(df['Close'][-1])
                }
                }
   
              requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=PICKERSHORT)    
         
            if (df['rsi'][-2] < 30) and (df['roc'][-2] < -3):           
              
             if (df['rsi'][-3] > df['rsi'][-2] < df['rsi'][-1]): 
               
              Tb.telegram_canal_3por(f"🟢 {symbol}\n🔝 Cambio: % {round(df['roc'][-2],2)} \n💵 Precio: {df['Close'][-2]}\n📍 Picker ▫️ 5 min") 
            
              PICKERLONG = {
               "name": "PICKER LONG",
               "secret": "xjth0i3qgb",
               "side": "buy",
               "symbol": symbol,
               "open": {
               "price": float(df['Close'][-1]) 
              }
              }
              requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=PICKERLONG) 
            
            #FISHING PISHA:
            if float(df['Close'][-2]) <= (df['ema_50'][-2]) and (ff > 0): 
            
              if (df['rsi'][-3] > 31) and (df['rsi'][-2] <= 29) and (df['adx'][-3] < df['adx'][-2]):   
                 
                Tb.telegram_canal_prueba(f"🔴 {symbol}\n💵 Precio: {df['Close'][-2]}\n🎣 Fishing Pisha ▫️ 5 min") 
            
                FISHINGSHORT = {
                "name": "FISHING SHORT",
                "secret": "azsdb9x719",
                "side": "sell",
                "symbol": symbol,
                "open": {
                "price": float(df['Close'][-1])
                }
                }
                requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT) 
            
              
            if float(df['Close'][-2]) >= (df['ema_50'][-2]) and (ff < 0): 
            
              if (df['rsi'][-3] < 69) and (df['rsi'][-2] >= 71) and (df['adx'][-3] < df['adx'][-2]): 
                   
                Tb.telegram_canal_prueba(f"🟢 {symbol}\n💵 Precio: {df['Close'][-2]}\n🎣 Fishing Pisha ▫️ 5 min")            
              
                FISHINGLONG = {
                "name": "FISHING LONG",
                "secret": "0kivpja7tz89",
                "side": "buy",
                "symbol": symbol,
                "open": {
                "price": float(df['Close'][-1])
                }
                }
   
                requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG)     
                
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
