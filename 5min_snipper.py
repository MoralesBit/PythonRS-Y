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

   
def calculate_indicators(symbol, interval):
        
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
    
    #VERIFICACION
    check = np.isin(1, df['diff_signal'][-10:])
    
    if check:
       check == 1 
    else : 
       check == 0
    
    df['check'] = check
 
    df['ema200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    acceleration=0.02 
    maximum=0.20
    
    df['psar'] = ta.SAR(df['High'], df['Low'], acceleration, maximum)
    
    df['psar_signal'] = np.where((df['psar'][-3] < df['Close'][-3] and df['psar'][-2] > df['Close'][-2]) or (df['psar'][-3] > df['Close'][-3] and df['psar'][-2] < df['Close'][-2]),1,0) 
    
    #VERIFICACION
    check = np.isin(1, df['psar_signal'][-5:])
    
    if check:
       check == 1 
    else : 
       check == 0
    
    df['check'] = check
        
    df['ema_short'] = np.where( df['ema200'] > df['Close'],1,0)
    df['ema_long'] = np.where( df['ema200'] < df['Close'],1,0)
    
    macd, signal, hist = ta.MACD(df['Close'], 
                                    fastperiod=12, 
                                    slowperiod=26, 
                                    signalperiod=9)
  
    df['macd'] = macd
    df['signal'] = signal
    df['hist'] = hist
    
    df['macd_long'] = np.where(df['macd'][-3] < df['signal'][-3] and df['macd'][-2] > df['signal'][-2] ,1,0)
    df['macd_short'] = np.where(df['macd'][-3] > df['signal'][-3] and df['macd'][-2] < df['signal'][-2] ,1,0)
    
    df['roc'] = ta.ROC(df['Close'], timeperiod=288)
    
    df['roc_long'] = np.where(df['roc'][-2] > 5,1,0)
    df['roc_short'] = np.where(df['roc'][-2] < -5,1,0)    
    
    return df[-4:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
        
        try:
            df = calculate_indicators(symbol,interval=Client.KLINE_INTERVAL_5MINUTE)
            dfbtc = calculate_indicators("BTCUSDT",interval=Client.KLINE_INTERVAL_5MINUTE)
            # revisando si seguir ema de BTC
            
                                                   
            if df is None:
                continue
            
            if df['roc_short'][-2] == 1:       
                if df['ema_short'][-2] == 1:
                    if df['check'][-2] == 1:
                        if df['macd_short'][-2] == 1:
                            
                            Tb.telegram_send_message(f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}\n📊 {round(df['roc'][-2],2)}% \n⏳ 5M")
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
              
                
            
            if df['roc_long'][-2] == 1:       
                if df['ema_long'][-2] == 1:
                    if df['check'][-2] == 1:
                        if df['macd_long'][-2] == 1:
                                                                       
                            Tb.telegram_send_message(f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}\n📊 {round(df['roc'][-2],2)}% \n⏳ 5M")
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
            
            if df['roc_short'][-2] == 1:       
                if df['ema_short'][-2] == 1:
                    if df['check'][-2] == 1:
                        if df['macd_long'][-2] == 1:
                            
                            Tb.telegram_canal_3por(f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}\n📊 {round(df['roc'][-2],2)}% \n⏳ 5M")
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
              
                
            if df['roc_long'][-2] == 1:       
                if df['ema_long'][-2] == 1:
                    if df['check'][-2] == 1:
                        if df['macd_short'][-2] == 1:
                            
                            Tb.telegram_canal_3por(f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}\n📊 {round(df['roc'][-2],2)}% \n⏳ 5M")
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
                                                                        
                                   
                                  
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
