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


#def get_trading_symbols():
   
    #with open('symbols_long.txt', 'r') as f:
    #    symbols = [line.strip() for line in f if line.strip()]
    #return symbols

def get_trading_symbols():
    """Obtiene la lista de símbolos de futuros de Binance que están disponibles para trading"""
    futures_info = client.futures_exchange_info()
    #symbols = [symbol['symbol'] for symbol in futures_info['symbols'] if symbol['status'] == "TRADING"]
    symbols = ["IMXUSDT","LEVERUSDT","ACHUSDT","AGLDUSDT"]
    coins_to_remove = ["ETHBTC", "USDCUSDT", "BNBBTC", "ETHUSDT", "BTCDOMUSDT", "BTCUSDT_230929","XEMUSDT","BLUEBIRDUSDT","ETHUSDT_231229","DOGEUSDT","LITUSDT","ETHUSDT_230929","BTCUSDT_231229","ETCUSDT"]  # Lista de monedas a eliminar
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
     
    df['ema50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    acceleration=0.025 
    maximum=0.20
        
    df['psar'] = ta.SAR(df['High'], df['Low'], acceleration, maximum)
    
    df['recompra_long'] = np.where( df['psar'][-2] < df['Close'][-2] and df['psar'][-1] > df['Close'][-1],1,0) 
     
    df['p_long'] = np.where(df['psar'][-2] < df['Close'][-2],1,0) 
        
    df['ema_long'] = np.where( df['ema50'] < df['Close'],1,0)
    
    df['roc'] = ta.ROC(df['Close'], timeperiod=288)
    
    df['roc_long'] = np.where(df['roc'][-2] > 7,1,0)
           
    df['vwma'] = ta.WMA(df['Close'], timeperiod=20)
  
    df['vwma_long'] = np.where(df['vwma'][-2] > df['psar'][-2] ,1,0)
    
    df['rsi'] = ta.RSI(df['Close'], timeperiod=14)
    
    df['rsi_sma'] = ta.SMA(df['rsi'], timeperiod=14)
    
    df['sma_signal'] = np.where(df['rsi_sma'][-2] < 65 ,1,0)
    
    df['vwav'] = ta.WMA(df['Close'], timeperiod=100)
    
    df['vwav_signal'] = np.where(df['vwav'] > df['ema50'] ,1,0)
     
    return df[-3:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
        
        try:
            df = calculate_indicators(symbol,interval=Client.KLINE_INTERVAL_5MINUTE)
            print(df['vwav'][-2])                                         
            if df is None:
                continue
           
            if df['ema_long'][-2] == 1:
                if df['vwma_long'][-2] == 1:
                    if df['p_long'][-2] == 1: 
                        if df['sma_signal'][-2] == 1:
                            if df['vwav_signal'][-2] == 1:      
                            
                                message = f"🟢 {symbol} \n💵 Precio: {df['Close'][-1]}"
                                Tb.telegram_canal_prueba(message)
                                              
                                Tendencia_Long = {
                                "name": "FISHING LONG",
                                "secret": "0kivpja7tz89",
                                "side": "buy",
                                "symbol": symbol,
                                "open": {
                                "price": float(df['Close'][-1])
                                }
                                }
                                requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=Tendencia_Long)    
                                 
            if df['recompra_long'][-1] == 1 :
                                            
                        message = f"🟢 {symbol} \n💵 Precio: {df['Close'][-1]}\n Recompra"
                        Tb.telegram_canal_prueba(message)
                                  
                        recompra_long = {
                        "name": "RECOMPRA LONG SHORT",
                        "secret": "luj6ewrkwje",
                        "side": "buy",
                        "symbol": symbol,
                        "open": {
                        "price": float(df['Close'][-1])
                        }
                        }
                        requests.post('https://hook.finandy.com/p-0RG59xlYnRP-A-qVUK', json=recompra_long)
            
            if df['vwav_signal'][-2] == 0:
                if df['recompra_long'][-2] == 1:
                    
                    message = f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}"
                    Tb.telegram_canal_3por(message)
                   
                    Contratendencia_short = {
                        "name": "PICKER SHORT",
                        "secret": "ao2cgree8fp",
                        "side": "sell",
                        "symbol": symbol,
                        "open": {
                        "price": float(df['Close'][-1]) 
                        }
                        }
            
                    requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=Contratendencia_short)            

        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
