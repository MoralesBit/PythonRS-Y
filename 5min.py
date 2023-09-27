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
                   
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
    
    df['sma'] = ta.SMA(df['Close'], timeperiod=20)
    
    df['highest_high'] = df['High'].max()
    df['lowest_low'] = df['Low'].min()
    df['diff_fib'] = df['highest_high'] - df['lowest_low']

    df['fib_23'] = df['Close'] - 0.236 * df['diff_fib']
    df['fib_61'] = df['Close'] - 0.618 * df['diff_fib']
    
    df['short'] = np.where(df['sma'] < df['fib_23'], 1, 0)
    df['long'] = np.where(df['sma'] < df['fib_61'], 1, 0)
    
    upperband, middleband, lowerband = ta.BBANDS(df['Close'], timeperiod=20, nbdevup=2.5, nbdevdn=2.5, matype=0)
    df['upperband'] = upperband
    df['middleband'] = middleband
    df['lowerband'] = lowerband
    
    df['up_signal'] = np.where(df['upperband'] <= df['Close'] ,1,0)
    df['low_signal'] = np.where(df['lowerband'] >= df['Close'] ,1,0)
        
    return df[-3:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
        print(symbol)

        try:
            df = calculate_indicators(symbol, interval=Client.KLINE_INTERVAL_5MINUTE)
            print(df['fib_23'][-2])
            print(df['fib_61'][-2]) 
            
            if df is None:
                continue
            
            if df['short'][-2] == 1:
                if df['up_signal'][-2] == 1:
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
                 
            
            if df['long'][-2] == 1:
                if df['low_signal'][-2] == 1: 
                
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
