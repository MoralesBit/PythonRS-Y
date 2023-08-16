import time
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
    #symbols = ["HIGHUSDT", "BLZUSDT", "1000SHIBUSDT", "1000PEPEUSDT","TLMUSDT", "APEUSDT", "ANTUSDT", "OXTUSDT"]
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
    upperband, middleband, lowerband = ta.BBANDS(df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['upperband'] = upperband
    df['middleband'] = middleband
    df['lowerband'] = lowerband
        
    df[['Open', 'High', 'Low', 'Close','Volume']] = df[['Open', 'High', 'Low', 'Close','Volume']].astype(float) 
    
    df['adl'] = (((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (df["High"] - df["Low"]))
        
    df['adl'] *= df['Volume']
    
    df['diff'] = abs((df['High'] / df['Low'] -1) * 100)
    
    df['cmf'] = pd.Series(df['adl']).rolling(20).sum() / pd.Series(df['Volume']).rolling(20).sum()
    
    df['rsi'] = ta.RSI(df['Close'], timeperiod=14)
    
    df['sma14'] = ta.SMA(df['rsi'], timeperiod=14)
    df['sma58'] = ta.SMA(df['rsi'], timeperiod=58)
       
    return df[-3:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
        
        try:
            df = calculate_indicators(symbol,interval=Client.KLINE_INTERVAL_5MINUTE)
           
                           
            if df is None:
                continue
            
            if df['sma14'][-3] > df['sma58'][-3] and df['sma14'][-2] < df['sma58'][-2]:
                if df['cmf'][-2] > 0:              
                    if df['upperband'][-2] < df['Close'][-2]:
                            Tb.telegram_canal_prueba(f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]} \n📶 Cambio: {round(df['diff'][-2],2)}%\n🕳 MF: {round(df['cmf'][-2],2)}\n📍 Picker ▫️ 5 min")
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
                            print("NO UPPER")                                
                   
                if df['sma14'][-3] < df['sma58'][-3] and df['sma14'][-2] > df['sma58'][-2]:
                    if df['cmf'][-2] < 0:
                        if df['lowerband'][-2] > df['Close'][-2]:
                            Tb.telegram_canal_prueba(f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}\n📶 Cambio: {round(df['diff'][-2],2)}%\n🕳 MF: {round(df['cmf'][-2],2)}\n📍 Picker ▫️ 5 min")
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
                            print("NO LOWER")                    
                           
                        
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
