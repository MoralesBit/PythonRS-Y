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
    #symbols = ["TOMOUSDT", "MTLUSDT", "QNTUSDT", "LDOUSDT","TRUUSDT", "HIGHUSDT", "SANDUSDT", "IDUSDT" , "MANAUSDT", "1000PEPEUSDT", "LITUSDT"]  
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
    
    fz=2.2
     
    upperband, middleband, lowerband = ta.BBANDS(df['Close'], timeperiod=20, nbdevup=fz, nbdevdn=fz, matype=0)
    df['upperband'] = upperband
    df['middleband'] = middleband
    df['lowerband'] = lowerband
    
    up_bb_30, mid_bb_30, low_bb_30 = ta.BBANDS(df['Close'], timeperiod=20, nbdevup=fz, nbdevdn=fz, matype=0)
    df['up_bb'] = up_bb_30
    df['mid_bb'] = mid_bb_30
    df['low_bb'] = low_bb_30
                   
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
    
    BB = (df['Close'] - df['lowerband']) / ( df['upperband'] - df['lowerband'])
    
    df['BB'] = BB
     
    rsi = ta.RSI(df['Close'], timeperiod=14)
    df['rsi'] = rsi 
      
    sma_period = 14
    
    df['rsi_sma'] = ta.SMA(df['rsi'], timeperiod=sma_period)
    
    cci = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=58)
    df['cci'] = cci
    
    df['cci_sma'] = ta.SMA(df['cci'], timeperiod=20)
    
    df['diff'] = abs((df['High'] / df['Low'] -1) * 100)
       
    return df[-3:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                    
        print(symbol)
        
        try:
            df = calculate_indicators(symbol)
            df_new = calculate_indicators("BTCUSDT") 
                                                                                              
            if df is None:
                continue
            # TENDENCIA MARCADA:
            if df_new['middleband'][-2] < df_new['Close'][-2]:
                if 0 > (df_new['cci'][-2] > df_new['cci_sma'][-2]):
                    if df['low_bb'][-2] > df['Close'][-2]:  
                    
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
                            print("No hay señales SHORT Fishing")        

                else:
                    print("No hay MERCA Fishing")
                
                       
            
            if df_new['middleband'][-2] > df_new['Close'][-2]:
                if 0 < (df_new['cci'][-2] < df_new['cci_sma'][-2]):
                    if df['up_bb'][-2] < df['Close'][-2]: 
                                                                      
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
                        print("No hay señales LONG Fishing")
                else:
                    print("No hay MERCA Fishing")
                            
            
            #CONTRATENDENCIA
            
            if df_new['upperband'][-2] < df_new['Close'][-2]:
                if df_new['cci'][-2] > 150 and df['cci'][-2] > 150 and df_new['cci_sma'][-2] > 50:
                    if df['upperband'][-2] < df['Close'][-2]:   
                        
                        Tb.telegram_canal_3por(f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}\n📍 Picker ▫️ 5 min")
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
                else:
                        print("No hay señales SHORT PICKER") 
             
            
            if df_new['lowerband'][-2] > df_new['Close'][-2]: 
                if df_new['cci'][-2] < -150 and df['cci'][-2] < -150 and df_new['cci_sma'][-2] < -50:
                    if df['upperband'][-2] > df['Close'][-2]:   
                   
                        Tb.telegram_canal_3por(f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}\n📍 Picker  ▫️ 5 min")
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
                        print("No hay señales LONG PICKER")
                        
            # TENDENCIA PRUEBA CON TOPES:
            if df_new['middleband'][-2] < df_new['Close'][-2]:
                if 0 > (df_new['cci'][-2] > df_new['cci_sma'][-2]):
                    if df['up_bb'][-2] < df['Close'][-2] and df['rsi'][-2] > 70:  
                    
                        Tb.telegram_canal_prueba(f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}\n🚀 Picker ▫️ 5 min")
                       
                    else:
                        print("No hay señales SHORT 🚀 Picker")
            
            if df_new['middleband'][-2] > df_new['Close'][-2]:
                if 0 < (df_new['cci'][-2] < df_new['cci_sma'][-2]):
                    if df['low_bb'][-2] > df['Close'][-2] and df['rsi'][-2] < 30: 
                                                                      
                        Tb.telegram_canal_prueba(f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}\n🚀 Picker ▫️ 5 min")
                    
                    else:
                        print("No hay señales LONG 🚀 Picker")         
                        
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
