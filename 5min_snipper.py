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
 
    df['diff'] = abs((df['High'] / df['Low'] -1) * 100)
    
    #long
    df['4l'] =  abs((df['High'][-4] / df['Close'][-4] -1) * 100) 
    df['2l'] =  abs((df['Open'][-2] / df['Low'][-2] -1) * 100) 
    
    #promedio long
    df['proml'] = (df['4l'] + df['2l'])/2
      
    df['pointl'] = (1-df['proml'] /100)* df['Open'][-2]
    
    #short
    df['4s'] =  abs((df['Close'][-4] / df['Low'][-4] -1) * 100) 
    df['2s'] =  abs((df['Open'][-2] / df['High'][-2] -1) * 100) 
    
    #promedio Short
    
    df['proms'] = (df['4s'] + df['2s'])/2
    
    df['points'] = (1-df['proms'] /100)* df['Open'][-2]
        
    return df[-4:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
       
        try:
            df = calculate_indicators(symbol,interval=Client.KLINE_INTERVAL_5MINUTE)

            if df is None:
                continue
            
            if df['diff'][-3] > 2:
                if df['upperband'][-3] <= df['Close'][-3]: 
                     
                            Tb.telegram_canal_prueba(f"🔴 {symbol} \n💵 Precio: {df['pointl'][-2]}")
                            PORSHORT = {
                            "name": "CORTO 3POR",
                            "secret": "ao2cgree8fp",
                            "side": "sell",
                            "symbol": symbol,
                            "open": {
                            "price": df['pointl'][-2]
                            }
                            }
   
                
                            requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT)
                else:
                            print("NO UPPER")                                
                   
                if df['lowerband'][-3] >= df['Close'][-3]:
                            Tb.telegram_canal_prueba(f"🟢 {symbol} \n💵 Precio: {df['pointl'][-2]}")
                            PORLONG = {
                            "name": "LARGO 3POR",
                            "secret": "nwh2tbpay1r",
                            "side": "buy",
                            "symbol": symbol,
                            "open": {
                            "price": df['pointl'][-2]
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
