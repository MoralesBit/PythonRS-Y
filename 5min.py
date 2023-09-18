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
    #symbols = ["TRBUSDT", "MTLUSDT", "SFPUSDT", "API3USDT"]
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
    
    df['diff'] = ((df['High'] / df['Low'] -1) * 100)
    
    df['diff_up'] = np.where((df['diff'][-2]) > 2 ,1,0)
    df['diff_down'] = np.where((df['diff'][-2]) < -2 ,1,0)
        
    acceleration=0.02 
    maximum=0.20
    
    df['psar'] = ta.SAR(df['High'], df['Low'], acceleration, maximum)
        
    df['roc'] = ta.ROC(df['Close'], timeperiod=288)
    
    df['roc_signal'] = np.where((df['roc'][-2]) > 5 or df['roc'][-2] < -5,1,0)
        
    df['diff_psar'] = abs((df['Open'] / df['psar'] -1) * 100)
     
    return df[-4:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
        
        try:
            df = calculate_indicators(symbol,interval=Client.KLINE_INTERVAL_5MINUTE)
            print(df['psar'][-2])
            in_Long = (df['Close'][-2] - (df['Close'][-2]*df['diff_psar'][-4]))
            in_short = (df['Close'][-2] + (df['Close'][-2]*df['diff_psar'][-4]))
            
                         
            if df is None:
                continue
                
            if df['diff_down'][-2] == 1:
                        
                            message = f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}\🔜 {round(in_Long,3)} \n💥 {round(df['diff_psar'][-4],2)}%"
                            Tb.telegram_canal_3por(message)
                                              
                            contratendencia_long = {
                            "name": "PICKER LONG",
                            "secret": "nwh2tbpay1r",
                            "side": "buy",
                            "symbol": symbol,
                            "open": {
                            "price": in_Long
                            }
                            }
                            requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=contratendencia_long)      
                               
            if df['diff_up'][-2] == 1:  
                         
                            message = f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}\n🔜 {round(in_short,3)} \n💥 {round(df['diff_psar'][-4],2)}%"
                            Tb.telegram_canal_3por(message)
                                  
                            contratendencia_short= {
                            "name": "PICKER SHORT",
                            "secret": "hgw3399vhh",
                            "side": "sell",
                            "symbol": symbol,
                            "open": {
                            "price": in_short
                            }
                            }
   
                            requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=contratendencia_short)
            
                        
              
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
