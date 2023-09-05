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
    symbols = ["FLMUSDT"]
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
      
    df['diff'] = abs((df['High'] / df['Low'] -1) * 100)
    df['diff_signal'] = np.where(df['diff'] > 4,1,0)
   
    
    df['retro_short'] = abs((df['High'] / df['Close'] -1) * 100) 
    df['restro_signal_short'] = np.where(0.60 > df['retro_short'][-1] > 0.5,1,0)
    df['retro_long'] = abs((df['Low'] / df['Close'] -1) * 100) 
    df['restro_signal_long'] = np.where(0.60 > df['retro_long'][-1] > 0.5,1,0)
    
    df['trix'] = ta.TRIX(df['Close'])
    df['trix_signal'] = np.where(df['trix'][-2] < df['trix'][-1],1,0)
    
      
    #df['rsi'] = ta.RSI(df['Close'], timeperiod=14)
      
    df['cci'] = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=28)
    df['cci_short'] = np.where(df['cci'][-2] > 250,1,0)
    df['cci_long'] = np.where(df['cci'][-2] < -250,1,0)
    
    return df[-3:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
        
        try:
            df = calculate_indicators(symbol,interval=Client.KLINE_INTERVAL_5MINUTE)
            print(df['diff'][-1])
            print(df['retro_short'][-1])
            print(df['retro_long'][-1])
                                                   
            if df is None:
                continue
           
            if df['diff_signal'][-1] == 1 and df['restro_signal_short'][-1] and df['trix_signal'][-1] == 0:
                Tb.telegram_canal_prueba(f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}\n🚀 Fast & Fury ")
                PORSHORT = {
                            "name": "PICKER SHORT",
                            "secret": "ao2cgree8fp",
                            "side": "sell",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-1]) 
                            }
                            }
   
                
                requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT)
                        
            if df['diff_signal'][-1] == 1 and df['restro_signal_long'][-1] and df['trix_signal'][-1] == 1:
                Tb.telegram_canal_prueba(f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}\n🚀 Fast & Fury")
                PORLONG = {
                            "name": "PICKER LONG",
                            "secret": "nwh2tbpay1r",
                            "side": "buy",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-1])
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
