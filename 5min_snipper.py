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
    #symbols = ["AMBUSDT", "BLZUSDT"]
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
    
    upperband, middleband, lowerband = ta.BBANDS(df['Close'], timeperiod=350, nbdevup=2.5, nbdevdn=2.5, matype=0)
    df['upperband'] = upperband
    df['middleband'] = middleband
    df['lowerband'] = lowerband
    
    df[['Open', 'High', 'Low', 'Close','Volume']] = df[['Open', 'High', 'Low', 'Close','Volume']].astype(float) 
    
    df['up'] = np.where(df['Close'] > df['upperband'], 1,0)
    df['down'] = np.where(df['Close'] < df['lowerband'], 1,0)
           
    
           
    acceleration=0.02 
    maximum=0.20
    
    df['psar'] = ta.SAR(df['High'], df['Low'], acceleration, maximum)
    
    df['p_short'] = np.where( df['psar'][-3] < df['Close'][-3] and df['psar'][-2] > df['Close'][-2],1,0) 
    df['p_long'] = np.where( df['psar'][-3] > df['Close'][-3] and df['psar'][-2] < df['Close'][-2],1,0) 

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
           
            if df['down'][-2] == 1:      
                    if df['p_short'][-2] == 1:
                            
                            Tb.telegram_send_message(f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}\n⏳ 5M \nBBup:{df['upperband'][-2]} \nBBlw:{df['lowerband'][-2]}")
                            FISHINGSHORT = {
                            "name": "FISHING SHORT",
                            "secret": "azsdb9x719",
                            "side": "sell",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-2])
                            }
                            }
                            requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT) 
              
            if df['up'][-2] == 1:      
                    if df['p_long'][-2] == 1:
                        
                                                                       
                            Tb.telegram_send_message(f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}\n⏳ 5M \nBBup:{df['upperband'][-2]} \nBBlw:{df['lowerband'][-2]}")
                            FISHINGLONG = {
                            "name": "FISHING LONG",
                            "secret": "0kivpja7tz89",
                            "side": "buy",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-2])
                            }
                            }
                            requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG)
                            
                     
            else :
                print("NEXT")       
            
            #time.sleep(0.5)                 
                           
                        
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
