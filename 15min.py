import time
import numpy as np
import requests
import pandas as pd
import talib as ta
from binance.client import Client
import Telegram_bot as Tb

Pkey = ''
Skey = ''
client = Client(api_key=Pkey, api_secret=Skey)

def get_trading_symbols():
    """Obtiene la lista de símbolos de futuros de Binance que están disponibles para trading"""
    with open('symbols.txt', 'r') as f:
        symbols = [line.strip() for line in f if line.strip()]
    return symbols
   
def calculate_indicators(symbol,interval):
        
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=1000)
    df = pd.DataFrame(klines)
    if df.empty:
        return None
    df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                  'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    
    df = df.set_index('Open time')
           
    df[['Open', 'High', 'Low', 'Close','Volume']] = df[['Open', 'High', 'Low', 'Close','Volume']].astype(float) 
          
    acceleration=0.02 
    maximum=0.20
    
    df['psar'] = ta.SAR(df['High'], df['Low'], acceleration, maximum)
    
    df['p_short'] = np.where( df['psar'][-2] < df['Close'][-2] and df['psar'][-1] > df['Close'][-1],1,0) 
    df['p_long'] = np.where( df['psar'][-2] > df['Close'][-2] and df['psar'][-1] < df['Close'][-1],1,0) 
     
    return df[-3:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
        
        try:
            df = calculate_indicators(symbol,interval=Client.KLINE_INTERVAL_5MINUTE)
                                                     
            if df is None:
                continue
           
            if df['p_long'][-1] == 1 :
             
                        message = f"🟢 {symbol} \n💵 Precio: {df['Close'][-1]} Recompra"
                        Tb.telegram_canal_prueba(message)
                                              
                        recompra_long = {
                        "name": "RECOMPRA LONG",
                        "secret": "luj6ewrkwje",
                        "side": "buy",
                        "symbol": symbol,
                        "open": {
                        "price": float(df['Close'][-1])
                        }
                        }
                        requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=recompra_long)    
                                 
            if df['p_short'][-1] == 1 :
              
                        message = f"🔴 {symbol} \n💵 Precio: {df['Close'][-1]} Recompra"
                        Tb.telegram_canal_prueba(message)
                                  
                        recompra_short = {
                        "name": "RECOMPRA SHORT",
                        "secret": "5vzf98rzhrf",
                        "side": "sell",
                        "symbol": symbol,
                        "open": {
                        "price": float(df['Close'][-1])
                        }
                        }
                        requests.post('https://hook.finandy.com/B5IDjcrXh2P_5OE-qVUK', json=recompra_short) 
                
       
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
