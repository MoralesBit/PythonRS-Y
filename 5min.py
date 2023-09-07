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
    futures_info = client.futures_exchange_info()
    #symbols = [symbol['symbol'] for symbol in futures_info['symbols'] if symbol['status'] == "TRADING"]
    symbols = ["PERPUSDT"]
    #symbols.remove("ETHBTC")  
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
      
    df['retro'] = abs((df['Open'] / df['Close'] -1) * 100) 
    df['retro_signal'] = np.where(df['retro'][-1] > 1,1,0)
    
    df['posicion_signal'] = np.where(df['Close'] < df['Open'],1,0)
    
    acceleration=0.02 
    maximum=0.20
    
    df['psar'] = ta.SAR(df['High'], df['Low'], acceleration, maximum)
    df['psar_signal'] = np.where(df['psar'] > df['Close'], 1,0)
    
    macd, signal, hist = ta.MACD(df['Close'], 
                                    fastperiod=12, 
                                    slowperiod=26, 
                                    signalperiod=9)
  
    df['macd'] = macd
    df['signal'] = signal
    df['hist'] = hist
    
    df['macd_long'] = np.where( df['hist'][-2] < df['hist'][-1],1,0)
    df['macd_short'] = np.where( df['hist'][-2] > df['hist'][-1],1,0)  

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
           
            if df['macd_short'][-1] == 1 and df['retro_signal'][-1] == 1 and df['posicion_signal'][-1] == 0:
                Tb.telegram_canal_prueba(f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}\n🚀 Fast and Fury")
                PORSHORT = {
                            "name": "PICKER SHORT",
                            "secret": "ao2cgree8fp",
                            "side": "sell",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Open'][-1]) 
                            }
                            }
   
                
                requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT)
                        
            if df['macd_long'][-1] == 0 and df['retro_signal'][-1] == 1 and df['posicion_signal'][-1] ==1:
                Tb.telegram_canal_prueba(f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}\n🚀 Fast and Fury")
                PORLONG = {
                            "name": "PICKER LONG",
                            "secret": "nwh2tbpay1r",
                            "side": "buy",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Open'][-1])
                            }
                            }
                requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG) 
            
            time.sleep(0.25)            
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 0.25 - current_time % 0.25
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
