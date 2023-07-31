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
    #symbols = ["BTCUSDT", "XRPUSDT", "BNBUSDT", "ADAUSDT","DOGEUSDT", "SOLUSDT", "TRXUSDT", "LTCUSDT" , "MATICUSDT", "BCHUSDT", "AVAXUSDT","1000SHIBUSDT","LINKUSDT","XLMUSDT","UNIUSDT","ATOMUSDT","XMRUSDT","FILUSDT"]  
    return symbols

def calculate_indicators(symbol):
        
    klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE, limit=500)
    df = pd.DataFrame(klines)
    if df.empty:
        return None
    df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                  'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    
    df = df.set_index('Open time')
    
    upperband, middleband, lowerband = ta.BBANDS(df['Close'], timeperiod=20, nbdevup=2.5, nbdevdn=2.5, matype=0)
    df['upperband'] = upperband
    df['middleband'] = middleband
    df['lowerband'] = lowerband
                     
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
    
    df['diff'] = abs((df['High'] / df['Low'] -1) * 100)
    
    cci = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=58)
    df['cci'] = cci
    
    df['cci_sma'] = ta.SMA(df['cci'], timeperiod=58)
    
    # Calcular los niveles de soporte y resistencia utilizando la función de la biblioteca TA-Lib
    n = 20  # Número de periodos utilizado para el cálculo
    df['support_levels'] = ta.SMA(df['Close'], n) - 2 * ta.STDDEV(df['Close'], n)
    df['resistance_levels'] = ta.SMA(df['Close'], n) + 2 * ta.STDDEV(df['Close'], n)
   
    return df[-3:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
        print(symbol)

        try:
            df = calculate_indicators(symbol)
            Close = float(df['Close'][-2])
            if df is None:
                continue
            
            if (df['resistance_levels'][-2] > df['Close'][-2]) and (df['cci_sma'][-2] > 100) and (df['diff'][-2] > 1): 
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
                 
            
            
            if (df['support_levels'][-2] > df['Close'][-2]) and (df['cci_sma'][-2] < -100) and (df['diff'][-2] > 1):
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
                    
            
                
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
