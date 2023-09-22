import time
import numpy as np
import requests
import pandas as pd
import talib as ta
from binance.client import Client
import Telegram_bot as Tb
import pandas_ta as tw


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
    symbols = [symbol['symbol'] for symbol in futures_info['symbols'] if symbol['status'] == "TRADING"]
    #symbols = ["IMXUSDT","LEVERUSDT","ACHUSDT","AGLDUSDT"]
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
    
    df['roc_signal'] = np.where(df['roc'][-2] > 5,1,0)
           
    df['vwma'] = ta.WMA(df['Close'], timeperiod=20)
  
    df['vwma_long'] = np.where(df['vwma'][-2] > df['psar'][-2] ,1,0)
    
    df['rsi'] = ta.RSI(df['Close'], timeperiod=14)
    
    df['rsi_sma'] = ta.SMA(df['rsi'], timeperiod=14)
    
    df['sma_signal'] = np.where(df['rsi_sma'][-2] < 65 ,1,0)
       
    df["vwav"] = tw.vwap(df['High'] , df['Low'], df['Close'] , df['Volume'])
        
    df['signal_short'] = np.where(df['vwav'][-2] < df['ema50'][-2] and df['vwav'][-1] > df['ema50'][-1] ,1,0)
    df['signal_long'] = np.where(df['vwav'][-2] > df['ema50'][-2] and df['vwav'][-1] < df['ema50'][-1] ,1,0)
    
     
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
            if df['roc_signal'][-2] == 1:               
                if df['signal_short'][-2] == 1:
                    
                    
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
                        
            if df['roc_signal'][-2] == 1:               
                if df['signal_long'][-2] == 1:
                    
                        
                        message = f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}"
                        
                        Tb.telegram_canal_3por(message)
                                      
                        Contratendencia_long = {
                        "name": "PICKER LONG",
                        "secret": "xjth0i3qgb",
                        "side": "buy",
                        "symbol": symbol,
                        "open": {
                        "price": float(df['Close'][-1])
                        }
                        }
                        requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=Contratendencia_long)             

        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
