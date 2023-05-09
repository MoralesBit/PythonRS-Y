import datetime
import time
import requests
import numpy as np
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
    return symbols

def calculate_indicators(symbol):
    """Calcula los indicadores de Bollinger para un símbolo y devuelve las últimas velas"""
    klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_3MINUTE, limit=1000)
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
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
    df['BB'] = (df['Close'] - df['lowerband']) / (df['upperband'] - df['lowerband'])
    df['diff'] = abs((df['High'] / df['Low'] - 1) * 100)
     
   
    return df.iloc[-3:]


def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
        

    for symbol in symbols:
        print(symbol)
        
        try:
            df = calculate_indicators(symbol)
            if df is None:
                continue
              #Imbalance
            
            def calculate_imbalance(symbol, depth=20):
                """
                    Calcula el desequilibrio para un símbolo dado utilizando el volumen acumulado en el libro de órdenes.
                """
                order_book = client.futures_order_book(symbol=symbol, limit=depth)
                bids = order_book['bids']
                asks = order_book['asks']

                bid_volume = sum([float(bid[1]) for bid in bids])
                ask_volume = sum([float(ask[1]) for ask in asks])

                total_volume = bid_volume + ask_volume

                if total_volume > 0:
                    imbalance = (ask_volume - bid_volume) / total_volume
                else:
                    imbalance = 0.0

                return imbalance
            
            imbalance = calculate_imbalance(symbol)
            
            if df.iloc[-2]['Close'] > df.iloc[-2]['upperband'] and df.iloc[-2]['diff'] >= 2 and imbalance < -0.55:
              Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(df['diff'][-3],2)} \n💵 Precio: {df['close'][-2]}\n📍 Picker: {round(imbalance,6)}")
              PORSHORT = {
    "name": "CORTO 3POR",
    "secret": "ao2cgree8fp",
    "side": "sell",
    "symbol": symbol,
    "open": {
    "price": df.iloc[-1]['Close']
    }
    }
   
              requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT)    
            elif df.iloc[-2]['Close'] < df.iloc[-2]['lowerband'] and df.iloc[-2]['diff'] >= 2 and imbalance > 0.55:
              Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(df['diff'][-3],2)} \n💵 Precio: {df['close'][-2]}\n📍 Picker: {round(imbalance,6)}") 
              PORLONG = {
    "name": "LARGO 3POR",
    "secret": "nwh2tbpay1r",
    "side": "buy",
    "symbol": symbol,
    "open": {
    "price": df.iloc[-1]['Close']
    }
    }
              requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG) 
        except Exception as e:
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 180 - current_time % 180
    time.sleep(seconds_to_wait)    
    run_strategy()
