import time
import requests
import numpy as np
import pandas as pd
import talib as ta
from binance.client import Client
import Telegram_bot as Tb
import pandas_ta as tw
 

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

def calculate_indicators(symbol, interval):
        
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=500)
    df = pd.DataFrame(klines)
    if df.empty:
        return None
    df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                  'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    
    df = df.set_index('Open time')
                   
    df[['Open', 'High', 'Low', 'Close','Volume']] = df[['Open', 'High', 'Low', 'Close','Volume']].astype(float)
       
    df['upperband'], df['middleband'], df['lowerband'] = ta.BBANDS(df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2)  
    
    df['up_signal'] = np.where(df['upperband'] <= df['Close'],1,0)
    df['low_signal'] = np.where(df['lowerband'] >= df['Close'],1,0)
    
    df['Volume'] = pd.to_numeric(df['Volume'])
    df['Close'] = pd.to_numeric(df['Close'])
    #Calcular el oscilador de volumen en porcentaje usando las longitudes corta y larga:
    df['Short Avg'] = df['Volume'].rolling(5).mean()
    df['Long Avg'] = df['Volume'].rolling(10).mean()
    df['Volume_Oscillator'] = ((df['Short Avg'] - df['Long Avg']) / df['Long Avg']) * 100
    df['vol_positivo'] = np.where(df['Volume_Oscillator'] >= 0,1,0)
    df['vol_negativo'] = np.where(df['Volume_Oscillator'][-3] >= 50 and df['Volume_Oscillator'][-2] < 50 ,1,0)

    df['15_Vol'] = np.where(df['vol_positivo'][-3] > 15 and df['vol_positivo'][-2] < 15,1,0)
    df['-15_Vol'] = np.where(df['vol_negativo'][-3] < -15 and df['vol_negativo'][-2] > -15,1,0)
    
    df['roc'] = ta.ROC(df['Close'], timeperiod=288)
    
    df['roc_long'] = np.where(df['roc'][-2] > 10,1,0)
    df['roc_short'] = np.where(df['roc'][-2] < -10,1,0)
     
    return df[-3:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
        print(symbol)

        try:
            df = calculate_indicators(symbol, interval=Client.KLINE_INTERVAL_5MINUTE)
            print(df['Volume_Oscillator'][-2])
           
            if df is None:
                continue
            
            if df['up_signal'][-2] == 1:
                
                if df['vol_negativo'][-2] == 1:
                        
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
                 
            if df['low_signal'][-2] == 1:
                
                if df['vol_positivo'][-2] == 1:
                        
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
                        
            if df['-15_Vol'][-2] == 1:
               
                if df['roc_long'][-2] == 1:
                        
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
                    
            if df['15_Vol'][-2] == 1:
               
                if df['roc_short'][-2] == 1:
                        
                        message = f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}\n📊 {round(df['roc'][-2],3)}% \n💥 {round(df['diff'][-2],2)}%"
                        Tb.telegram_canal_prueba(message)
                                  
                        Tendencia_short = {
                            "name": "FISHING SHORT",
                            "secret": "azsdb9x719",
                            "side": "sell",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-2])
                            }
                            }
                        requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=Tendencia_short)                                                                                 
       
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    #time.sleep(seconds_to_wait)    
    run_strategy()
