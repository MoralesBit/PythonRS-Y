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
    
    fz=2
     
    upperband, middleband, lowerband = ta.BBANDS(df['Close'], timeperiod=20, nbdevup=fz, nbdevdn=fz, matype=0)
    df['upperband'] = upperband
    df['middleband'] = middleband
    df['lowerband'] = lowerband
   
    df['diff'] = abs((df['High'] / df['Low'] -1) * 100)
    
    df['rsi'] = ta.RSI(df['Close'], timeperiod=5)
    df['SRSI'] = ta.SMA(df['rsi'], timeperiod=14)
    
    # Calcular el Standard Deviation (STD) de los precios de cierre
    n = 14  # Número de períodos para el STD
    std = ta.STDDEV(df['Close'], timeperiod=n, nbdev=1)    
    # Calcular el Relative Volatility Index (RVI) utilizando la función RSI de TA-Lib
    rvi = ta.RSI(std, timeperiod=5)
    df['rvi'] = rvi
    df['SRVI'] = ta.SMA(df['rvi'], timeperiod=14)
    
    cci = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=58)
    df['cci'] = cci

    return df[-3:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
        print(symbol)
        
        try:
            df = calculate_indicators(symbol)
                                                                             
            if df is None:
                continue
            
            
            if df['rsi'][-3] > 70 and df['rvi'][-3] > 80:
                
                if df['SRSI'][-2] >= df['rsi'][-2]:
                    
                    if df['upperband'][-2] < df['Close'][-2]:
                      
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
            
            
            if df['rsi'][-3] < 30 and df['rvi'][-3] < 20: 
                
                if df['SRSI'][-2] <= df['rsi'][-2]: 
                    
                    if df['lowerband'][-2] > df['Close'][-2]: 
                                                                         
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
