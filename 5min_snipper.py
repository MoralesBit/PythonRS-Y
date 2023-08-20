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
       
    #RSI
    df['rsi'] = ta.RSI(df['Close'], timeperiod=14)
    df['srsi'] = ta.SMA(df['rsi'], timeperiod= 20)
    
    df['60upcross'] = np.where( 60 > df['srsi'][-3] and  60 < df['srsi'][-2],1,0)
    df['60downcross'] = np.where( 60 < df['srsi'][-3] and  60 > df['srsi'][-2],1,0)
    
    df['40upcross'] = np.where( 40 > df['srsi'][-3] and 40 < df['srsi'][-2],1,0)
    df['40downcross'] = np.where( 40 < df['srsi'][-3] and 40 > df['srsi'][-2],1,0)
    
    #SIGNAL
    df['signal'] = np.where(df['diff'] >= 3,1,0)
    
    #VERIFICACION
    check = np.isin(1, df['signal'][-30:])
    
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
                
                if (df['60downcross'][-2] == 1):
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
                                                
                   
                if (df['40upcross'][-2] == 1):
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
                        
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 60 - current_time % 60
    time.sleep(seconds_to_wait)    
    run_strategy()
