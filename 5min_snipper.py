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
           
    df[['Open', 'High', 'Low', 'Close','Volume']] = df[['Open', 'High', 'Low', 'Close','Volume']].astype(float) 
      
    df['diff'] = abs((df['High'] / df['Low'] -1) * 100)
    df['diff_signal'] = np.where(df['diff'] > 3,1,0)
    
    upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                                timeperiod=20,
                                                nbdevup=3,
                                                nbdevdn=3,
                                                matype=0)
    df['upperband'] = upperband
    df['middleband'] = middleband
    df['lowerband'] = lowerband
    
    df['BB_signal_short'] = np.where(df['upperband'] < df['Close'],1,0)
    df['BB_signal_long'] = np.where(df['lowerband'] > df['Close'],1,0)
    
    df['rsi'] = ta.RSI(df['Close'], timeperiod=14)
    df['rsi_signal_short'] = np.where(df['rsi'] > 70,1,0)
    df['rsi_signal_long'] = np.where(df['rsi'] < 30,1,0)
    
    df['ema20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['ema200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    acceleration=0.02 
    maximum=0.20
    
    df['psar'] = ta.SAR(df['High'], df['Low'], acceleration, maximum)
    
    df['p_short'] = np.where( df['psar'][-3] < df['Close'][-3] and df['psar'][-2] > df['Close'][-2],1,0) 
    df['p_long'] = np.where( df['psar'][-3] > df['Close'][-3] and df['psar'][-2] < df['Close'][-2],1,0) 
    
    df['ema_short'] = np.where( df['ema200'] > df['Close'],1,0)
    df['ema_long'] = np.where( df['ema200'] < df['Close'],1,0)
    
    df['ema_short_20'] = np.where( df['ema20'] < df['Close'],1,0)
    df['ema_long_20'] = np.where( df['ema20'] > df['Close'],1,0)
    
    df['roc'] = ta.ROC(df['Close'], timeperiod=288)
    
    df['roc_long'] = np.where(df['roc'][-2] > 5,1,0)
    df['roc_short'] = np.where(df['roc'][-2] < -5,1,0)
    
    df['cci'] = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=28)
    df['cci_signal'] = np.where(df['cci'][-2] > 0,1,0)
    
    return df[-3:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
        
        try:
            df = calculate_indicators(symbol,interval=Client.KLINE_INTERVAL_5MINUTE)
            #dfbtc = calculate_indicators("BTCUSDT",interval=Client.KLINE_INTERVAL_5MINUTE)
            # revisando si seguir ema de BTC
                                                   
            if df is None:
                continue
            
            #if dfbtc['ema_short'][-2] == 1:      
            if df['p_long'][-2] == 1 and df['ema_short'][-2] == 1:
                if df['roc_short'][-2] == 1 and df['cci_signal'][-2] == 0 and df['ema_short_20'][-2] == 1:
                        Tb.telegram_send_message(f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}\n📊 {round(df['roc'][-2],3)}% \n⏳ 5M")
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
              
                
            
            if df['p_short'][-2] == 1 and df['ema_long'][-2] == 1:
                if df['roc_long'][-2] == 1  and df['cci_signal'][-2] == 1 and df['ema_long_20'][-2] == 1:                                             
                        Tb.telegram_send_message(f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}\n📊 {round(df['roc'][-2],3)}% \n⏳ 5M")
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
            
            if df['BB_signal_short'][-2] == 1 :
                if df['diff_signal'][-2] == 1 and df['rsi_signal_short'][-2] == 1:
                        Tb.telegram_canal_3por(f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}\n📊 {round(df['roc'][-2],3)}% \n⏳ 5M")
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
              
                
            if df['BB_signal_long'][-2] == 1 :
                if df['diff_signal'][-2] == 1 and df['rsi_signal_long'][-2] == 1:                                            
                        Tb.telegram_canal_3por(f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}\n📊 {round(df['roc'][-2],3)}% \n⏳ 5M")
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
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
