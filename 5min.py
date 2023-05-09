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
    
    return df[-3:]
  
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
    
    for symbol in symbols:
        print(symbol)
                
        try:
            df = calculate_indicators(symbol)
            if df is None:
                continue
                       
            #if df.iloc[-3]['Close'] > df.iloc[-3]['upperband'] and df.iloc[-2]['Close'] < df.iloc[-2]['upperband'] and df.iloc[-3]['diff'] >= 2:
            if (df['Close'][-3] > df['upperband'][-3]) and (df['Low'][-2] < df['upperband'][-2]) and (df['diff'][-3] >= 2):  
              Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 5 min \n🔝 Cambio: % {round(df['diff'][-3],2)} \n💵 Precio: {df['Close'][-2]}\n📍 Picker: {round(df['Open'][-2],6)}")
            
              PICKERSHORT= {
                "name": "PICKER SHORT",
                "secret": "hgw3399vhh",
                "side": "sell",
                "symbol": symbol,
                "open": {
                "price": float(df['Close'][-2])
                }
                }
   
              requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=PICKERSHORT)    
         
            #elif df.iloc[-3]['Close'] < df.iloc[-3]['lowerband'] and df.iloc[-2]['Close'] > df.iloc[-2]['lowerband'] and df.iloc[-3]['diff'] >= 2:
            if (df['Close'][-3] < df['lowerband'][-3]) and (df['High'][-2] > df['lowerband'][-2]) and (df['diff'][-3] >= 2): 
              Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 5 min \n🔝 Cambio: % {round(df['diff'][-3],2)} \n💵 Precio: {df['Close'][-2]}\n📍 Picker: {round(df['Open'][-2],6)}") 
            
              PICKERLONG = {
               "name": "PICKER LONG",
               "secret": "xjth0i3qgb",
               "side": "buy",
               "symbol": symbol,
               "open": {
               "price": float(df['Close'][-2]) 
              }
              }
              requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=PICKERLONG) 
        
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
