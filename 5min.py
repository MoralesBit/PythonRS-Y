import time
import requests
import numpy as np
import pandas as pd
from binance.client import Client

Pkey = ''
Skey = ''
n = 5
client = Client(api_key=Pkey, api_secret=Skey)

def get_trading_symbols():
    """Obtiene la lista de símbolos de futuros de Binance que están disponibles para trading"""
    with open('symbols.txt', 'r') as f:
        symbols = [line.strip() for line in f if line.strip()]
    return symbols
   
def calculate_indicators(symbol):
        
    klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE, limit=1000)
    df = pd.DataFrame(klines)
    if df.empty:
        return None
    df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                  'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    
    df = df.set_index('Open time')
             
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
          
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
                           
            if (df['Close'][-1]):
                            
                            SHORT = {
                            "name": "SHORT",
                            "secret": "wjd0pfjn24p",
                            "side": "sell",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-1])
                                }
                            }
   
                            requests.post('https://hook.finandy.com/TUxsdJn-Or-Nys7zqFUK', json=SHORT)
            
            if (df['Close'][-1]):                               
                            
                            LONG = {
                            "name": "LONG",
                            "secret": "an0rvlxehbn",
                            "side": "buy",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-1])
                                }
                            }
                            requests.post('https://hook.finandy.com/9nQNB3NdMGaoK-xWqVUK', json=LONG)                                              
          
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = n - current_time % n
    time.sleep(seconds_to_wait)    
    run_strategy()
    #todoslosderechosreservados
    #telegram: https://t.me/scalpingbitbot
