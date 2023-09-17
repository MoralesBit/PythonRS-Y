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
    symbols = ["BAKEUSDT", "PERPUSDT", "AUDIOUSDT", "SSVUSDT"]
    coins_to_remove = ["DOGEUSDT"]  # Lista de monedas a eliminar
    for coin in coins_to_remove:
        if coin in symbols:
            symbols.remove(coin)
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
    
    df['ema200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    df['ema_long'] = np.where( df['ema200'] > df['Close'],1,0)
    df['ema_short'] = np.where( df['ema200'] < df['Close'],1,0)
        
    acceleration=0.005 
    maximum=0.08
    
    df['psar'] = ta.SAR(df['High'], df['Low'], acceleration, maximum)
    
    df['p_short'] = np.where(df['psar'][-2] > df['Close'][-2],1,0) 
    df['p_long'] = np.where(df['psar'][-2] < df['Close'][-2],1,0) 
    
    df['psar_signal'] = np.where( df['psar'][-3] < df['Close'][-3] and df['psar'][-2] > df['Close'][-2],1,0) 
     
    df['roc'] = ta.ROC(df['Close'], timeperiod=288)
    
    df['roc_signal'] = np.where(abs(df['roc'][-2]) > 5,1,0)
        
    df['diff'] = abs((df['Close'] / df['psar'] -1) * 100)
     
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

            if df['ema_long'][-2] ==1 and df['psar_signal'][-2] == 1:
                        
                            message = f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}\n📊 {round(df['roc'][-2],3)}% \n💥 {round(df['diff'][-2],2)}%"
                            Tb.telegram_canal_3por(message)
                                              
                            Tendencia_Long = {
                            "name": "FISHING LONG",
                            "secret": "0kivpja7tz89",
                            "side": "buy",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-2])
                            }
                            }
                            requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=Tendencia_Long)    
                               
            if df['ema_short'][-2] ==1 and df['psar_signal'][-2] == 1:  
                         
                            message = f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}\n📊 {round(df['roc'][-2],3)}% \n💥 {round(df['diff'][-2],2)}%"
                            Tb.telegram_canal_3por(message)
                                  
                            Tendencia_short = {
                            "name": "FISHING SHORT",
                            "secret": "azsdb9x719",
                            "side": "sell",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-2])
                            }
                            }
                            requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=Tendencia_short) 
              
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
