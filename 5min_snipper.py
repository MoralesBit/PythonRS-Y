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
      
    df['diff'] = abs((df['Open'] / df['Close'] -1) * 100)
    
    df['roc'] = ta.ROC(df['Close'], timeperiod=288)
    
    df['mfi14'] = ta.MFI(df['High'], df['Low'], df['Close'], df['Volume'], timeperiod=14)
    df['mfi50'] = ta.MFI(df['High'], df['Low'], df['Close'], df['Volume'], timeperiod=50)  
    
    df['signal_long'] = np.where(df['mfi14'] > 80,1,0)
    df['signal_short'] = np.where(df['mfi14'] < 20,1,0)
    
    df['upcross'] = np.where( df['mfi50'][-3] > df['mfi14'][-3] and  df['mfi50'][-2] < df['mfi14'][-2],1,0)
    df['downcross'] = np.where( df['mfi50'][-3] < df['mfi14'][-3] and  df['mfi50'][-2] > df['mfi14'][-2],1,0)
           
       
    #VERIFICACION
    check_up = np.isin(1, df['upcross'][-30:])
    
    if check_up:
       check_up == 1 
    else : 
       check_up == 0
    
    df['check_up'] = check_up
    
     #VERIFICACION
    check_dwn = np.isin(1, df['downcross'][-30:])
    
    if check_dwn:
       check_dwn == 1 
    else : 
       check_dwn == 0
    
    df['check_dwn'] = check_dwn
              
    return df[-3:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
        
        try:
            df = calculate_indicators(symbol,interval=Client.KLINE_INTERVAL_1MINUTE)
            print(df['check_up'][-2]) 
            print(df['check_dwn'][-2])                                      
            if df is None:
                continue
            
            
            if df['roc'][-2] < -5:    
                if (df['check_dwn'][-2] == 1):
                    if  (df['signal_short'][-2] == 1):
                            Tb.telegram_canal_3por(f"🔴 {symbol} \n💵 Precio Entrada: {df['Close'][-2]}\n📍 Picker")
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
                                                
            if df['roc'][-2] > 5:       
                if (df['check_up'][-2] == 1):
                    if  (df['signal_long'][-2] == 1):
                            Tb.telegram_canal_3por(f"🟢 {symbol} \n💵 Precio Entrada: {df['Close'][-2]}\n📍 Picker")
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
                            
                           
                        
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 60 - current_time % 60
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
