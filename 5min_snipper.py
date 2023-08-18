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
    symbols = [symbol['symbol'] for symbol in futures_info['symbols'] if symbol['status'] == "TRADING"]
    #symbols = ["HIGHUSDT", "BLZUSDT", "1000SHIBUSDT", "1000PEPEUSDT","TLMUSDT", "APEUSDT", "ANTUSDT", "OXTUSDT"]
    symbols.remove("ETHBTC")  
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
    
    df['cci']  = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=58)
    df['scci'] = ta.SMA(df['cci'], timeperiod= 20)
    
    df['rsi'] = ta.RSI(df['Close'], timeperiod=14)
    df['rsi_upcross'] = np.where( df['rsi'][-3] < 80 and  df['rsi'][-2] > 80,1,0)
    df['rsi_downcross'] = np.where( df['rsi'][-3] > 20 and  df['rsi'][-2] < 20,1,0)
    
    df['signal'] = np.where(df['diff'] >= 3,1,0)
    
    df['cci_downcross'] = np.where(df['scci'][-3] < df['cci'][-3] and df['scci'][-2] > df['cci'][-2],1,0)
    df['cci_upcross'] = np.where(df['scci'][-3] > df['cci'][-3] and df['scci'][-2] < df['cci'][-2],1,0)
    
    check = np.isin(1, df['signal'][-10:])
    
    if check:
       check == 1 
    else : 
       check == 0
    
    df['check'] = check
   
           
    return df[-3:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
        
        try:
            df = calculate_indicators(symbol,interval=Client.KLINE_INTERVAL_1MINUTE)
            print(df['check'][-2])
                                       
            if df is None:
                continue
            
            if df['check'][-2]:
                
                if df['rsi_upcross'][-2] == 1:
                            Tb.telegram_canal_prueba(f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}")
                            PORSHORT = {
                            "name": "CORTO 3POR",
                            "secret": "ao2cgree8fp",
                            "side": "sell",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-2]) 
                            }
                            }
   
                
                            requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT)
                                                
                   
                if df['rsi_downcross'][-2] == 1:
                            Tb.telegram_canal_prueba(f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}")
                            PORLONG = {
                            "name": "LARGO 3POR",
                            "secret": "nwh2tbpay1r",
                            "side": "buy",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-2])
                            }
                            }
                            requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG)      
                else:
                            print("NO LOWER")                    
                           
                        
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
