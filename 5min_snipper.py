import time
import requests
import numpy as np
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
    #symbols = ["BTCUSDT", "XRPUSDT", "BNBUSDT", "ADAUSDT","DOGEUSDT", "SOLUSDT", "TRXUSDT", "LTCUSDT" , "MATICUSDT", "BCHUSDT", "AVAXUSDT","1000SHIBUSDT","LINKUSDT","XLMUSDT","UNIUSDT","ATOMUSDT","XMRUSDT","FILUSDT"]  
    return symbols

def calculate_indicators(symbol):
        
    klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE, limit=1000)
    df = pd.DataFrame(klines)
    if df.empty:
        return None
    df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                  'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    
    df = df.set_index('Open time')
                          
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
    
    upperband, middleband, lowerband = ta.BBANDS(df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['upperband'] = upperband
    df['middleband'] = middleband
    df['lowerband'] = lowerband
    
    # Calcular los niveles de soporte y resistencia utilizando la función de la biblioteca TA-Lib
    n = 20  # Número de periodos utilizado para el cálculo
    df['support_levels'] = ta.SMA(df['Close'], n) - 2 * ta.STDDEV(df['Close'], n)
    df['resistance_levels'] = ta.SMA(df['Close'], n) + 2 * ta.STDDEV(df['Close'], n)
    
    df['adx'] = ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)   
    
    return df[-4:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
        print(symbol)
       
        
        try:
            df = calculate_indicators(symbol)
            print(df['resistance_levels'][-2])
            print(df['support_levels'][-2])                                                                
            
            if df is None:
                continue
                      
            if df['support_levels'][-4] > df['Close'][-4]: 
                
                if df['Close'][-3] < df['Open'][-3] and df['Close'][-2] < df['Open'][-2]:
                    
                    if  df['adx'][-2] > 40:
                          
                            Tb.telegram_send_message(f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}\n📍 Fishing Pisha ▫️ 5 min")
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
                    else:
                            print("No Cumple")        
            
            if df['resistance_levels'][-4] < df['Close'][-4]:
                  
                if df['Close'][-3] > df['Open'][-3] and df['Close'][-2] > df['Open'][-2]:
            
                    if  df['adx'][-2] < 20:          
                                                                   
                            Tb.telegram_send_message(f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}\n📍 Fishing Pisha ▫️ 5 min")
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
                    
                    else:
                            print("No Cumple")
                
            
            if df['resistance_levels'][-2] > df['Close'][-2]: 
                
                if df['upperband'][-2] < df['Close'][-2]:
                    
                    if df['adx'][-2] > 40:
                          
                            Tb.telegram_canal_3por(f"🔴 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}\n📍 Picker ▫️ 5 min")
                            PICKERSHORT = {
                            "name": "PICKER SHORT",
                            "secret": "ao2cgree8fp",
                            "side": "sell",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-1]) 
                            }
                            }
   
                            requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PICKERSHORT) 
                    else:
                            print("No Cumple")        
            
            if df['support_levels'][-2] > df['Close'][-2]:
                  
                if df['lowerband'][-2] > df['Close'][-2]:
            
                    if  df['adx'][-2] < 20:          
                                                                   
                            Tb.telegram_canal_3por(f"🟢 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}\n📍 Picker  ▫️ 5 min")
                            PICKERLONG = {
                            "name": "PICKER LONG",
                            "secret": "nwh2tbpay1r",
                            "side": "buy",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-1])
                            }
                            }
                            requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PICKERLONG)                                               
                    
                    else:
                            print("No Cumple")
                
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
