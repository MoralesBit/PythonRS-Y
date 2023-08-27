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
    
    slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=14, slowd_matype=0)
    df['slowk'] = slowk
    df['slowd'] = slowd
    
    df['rsi'] = ta.RSI(df['Close'], timeperiod=14)
    
    acceleration=0.02 
    maximum=0.20
    
    df['psar'] = ta.SAR(df['High'], df['Low'], acceleration, maximum)
      
    df['short_signal'] = np.where( df['slowk'][-3] > df['slowd'][-3] and  df['slowk'][-2] < df['slowd'][-2],1,0)
    df['long_signal'] = np.where( df['slowk'][-3] < df['slowd'][-3] and  df['slowk'][-2] > df['slowd'][-2],1,0)
    df['psar_short'] = np.where( df['psar'] < df['Close'],1,0) 
    df['psar_long'] = np.where( df['psar'] > df['Close'],1,0) 
           
       
    #SIGNAL
    df['signal'] = np.where(df['diff'] >= 2,1,0)
    
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
                    
                if  (df['short_signal'][-2] == 1) and (df['psar_short'][-2] == 1):
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
                                                
                   
            
                if  (df['long_signal'][-2] == 1) and (df['psar_long'][-2] == 1):
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
