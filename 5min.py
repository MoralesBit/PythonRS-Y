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
    #symbols = ["IMXUSDT","LEVERUSDT","ACHUSDT","AGLDUSDT"]
    coins_to_remove = ["ETHBTC", "USDCUSDT", "BNBBTC", "ETHUSDT", "BTCDOMUSDT", "BTCUSDT_230929","XEMUSDT","BLUEBIRDUSDT","ETHUSDT_231229","DOGEUSDT","LITUSDT","ETHUSDT_230929","BTCUSDT_231229","ETCUSDT"]  # Lista de monedas a eliminar
    for coin in coins_to_remove:
        if coin in symbols:
            symbols.remove(coin)
    return symbols
   
def calculate_indicators(symbol):
        
    klines = client.futures_klines(symbol=symbol,interval=Client.KLINE_INTERVAL_5MINUTE, limit=1000)
    df = pd.DataFrame(klines)
    if df.empty:
        return None
    df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                  'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    
    df = df.set_index('Open time')
    df[['Open', 'High', 'Low', 'Close','Volume']] = df[['Open', 'High', 'Low', 'Close','Volume']].astype(float)
    
    df['diff'] = abs((df['High'] / df['Low'] -1) * 100)
  
    df['roc'] = ta.ROC(df['Close'], timeperiod=288)
    
    cci = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=58)
    df['cci'] = cci
                          
    return df[-5:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
        
        try:
           
            df = calculate_indicators(symbol)
            print(df['diff'][-2])
                                             
            if df is None:
                continue
            
            if df['diff'][-2] >= 2: 
                if df['cci'][-3] > 0 and df['cci'][-2] < 0 and  df['roc'][-1] > 10:
                                         
                    Tb.telegram_send_message(f"🟢 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}")
                    
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
                    
            if df['diff'][-2] >= 2: 
                if df['cci'][-3] < 0 and df['cci'][-2] > 0 and  df['roc'][-1] < -10:
                    Tb.telegram_send_message(f"🔴 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}")
                    
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
                        

        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
