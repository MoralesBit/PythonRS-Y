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
    #symbols = ["HIGHUSDT", "BLZUSDT", "1000SHIBUSDT", "1000PEPEUSDT","TLMUSDT", "APEUSDT", "ANTUSDT", "OXTUSDT"]
    symbols.remove("ETHBTC","ETHUSDT_230929","ETHUSDT","ETCUSDT","BLUEBIRDUSDT","USDCUSDT","XTZUSDT","XMRUSDT")  
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
    
    upperband, middleband, lowerband = ta.BBANDS(df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['upperband'] = upperband
    df['middleband'] = middleband
    df['lowerband'] = lowerband
    
    df['rsi'] = ta.RSI(df['Close'], timeperiod=14)
        
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
       
    df['ema_50'] = df['Close'].ewm(span=50, adjust=False).mean()
   
    return df[-3:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
        
        try:
            df = calculate_indicators(symbol,interval=Client.KLINE_INTERVAL_5MINUTE)
            df_4h = calculate_indicators(symbol, interval=Client.KLINE_INTERVAL_4HOUR)
            df_1h = calculate_indicators(symbol, interval=Client.KLINE_INTERVAL_1HOUR)  
                                                                                              
            if df is None:
                continue
           
            #CONTRATENDENCIA
            time.sleep(0.5)
            if df_4h['ema_50'][-1] > df_4h['Close'][-1]:
                if [df_1h['ema_50'][-1] > df_1h['Close'][-1]]:
                    if df['Close'][-2] >= df['upperband'][-2]:
                        if df['rsi'][-2] >= 70:
     
                            Tb.telegram_canal_3por(f"🔴 {symbol} \n💵 Precio: {df['Close'][-1]}\n📍 Picker ▫️ 5 min")
                            PORSHORT = {
                            "name": "CORTO 3POR",
                            "secret": "ao2cgree8fp",
                            "side": "sell",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-1]) 
                            }
                            }
   
                
                            requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT)
                        else:
                            print("RSI NO")                    
                    else:
                        print("BB NO")                
                else:
                    print("1H NO")                       
                    
            elif  df_4h['ema_50'][-1] < df_4h['Close'][-1]:  
                if [df_1h['ema_50'][-1] < df_1h['Close'][-1]]:
                    if df['Close'][-2] <= df['lowerband'][-2]:
                        if df['rsi'][-2] <= 30:
                    
                            Tb.telegram_canal_3por(f"🟢 {symbol} \n💵 Precio: {df['Close'][-1]}\n📍 Picker  ▫️ 5 min")
                            PORLONG = {
                            "name": "LARGO 3POR",
                            "secret": "nwh2tbpay1r",
                            "side": "buy",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-1])
                            }
                            }
                            requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG)      
                        else:
                            print("RSI NO")                    
                    else:
                        print("BB NO")
                else:
                    print("1H NO")             
                        
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
