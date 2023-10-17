import time
import numpy as np
import requests
import pandas as pd
import talib as ta
from binance.client import Client
import Telegram_bot as Tb
from talib import STOCH

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
    
    slowk, slowd = STOCH(df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=14, slowk_matype=0, slowd_period=14, slowd_matype=0)
    # Calcular la media móvil simple con smooth=3
    slowk_smooth = ta.SMA(slowk, 3)
    slowd_smooth = ta.SMA(slowd, 3)

# Asignar los valores al DataFrame
    df['slowk'] = slowk_smooth
    df['slowd'] = slowd_smooth
    
    df['roc'] = ta.ROC(df['Close'], timeperiod=288)
    
    df['roc_positivo'] = np.where(5 < df['roc'][-2] < 10,1,0)
    df['roc_negativo'] = np.where(-5 > df['roc'][-2] > -8,1,0)
                  
    return df
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
        
        try:
           
            df = calculate_indicators(symbol)
            print(df['slowk'][-2])
            print(df['slowd'][-2])
            print(df['roc_positivo'][-2])
            print(df['roc_negativo'][-2])
                                                                       
            if df is None:
                continue
            
            if df['slowk'][-2] < 40 and df['slowk'][-3] < df['slowd'][-3] and df['slowk'][-2] > df['slowd'][-2]:
                if df['roc_positivo'][-2] == 1:                   
                                      
                    Tb.telegram_canal_prueba(f"🟢 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}")
                    
            if df['slowk'][-2] > 60 and df['slowk'][-3] > df['slowd'][-3] and df['slowk'][-2] < df['slowd'][-2]:                     
                if df['roc_negativo'][-2] == 1:
                                
                        Tb.telegram_canal_prueba(f"🔴 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}")
                        

        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
