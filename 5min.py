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
    coins_to_remove = ["ETHBTC", "USDCUSDT", "BNBBTC", "ETHUSDT", "BTCDOMUSDT", "BTCUSDT_230929","XEMUSDT","BLUEBIRDUSDT","ETHUSDT_231229","DOGEUSDT","LITUSDT","ETHUSDT_230929","BTCUSDT_231229"]  # Lista de monedas a eliminar
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

    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    
    df['diff'] = abs((df['High'] / df['Low'] -1) * 100)
      
    precio_high = (max(df['Close']))
    precio_low = (min(df['Close']))
    diff_precio = precio_high - precio_low
    
    df['nivel_062'] = precio_high - (0.62)*(diff_precio)
    df['nivel_236'] = precio_high - (0.236)*(diff_precio)
    
    df['short'] = np.where(df['nivel_062'][-3] < df['Close'][-3] and df['nivel_062'][-2] > df['Close'][-2],1,0)
    df['long'] = np.where(df['nivel_236'][-3] > df['Close'][-3] and df['nivel_236'][-2] < df['Close'][-2],1,0)
    
    acceleration=0.02
    maximum=1

    df['psar'] = ta.SAR(df['High'], df['Low'], acceleration, maximum)

    df['p_short'] = np.where(df['psar'] > df['Close'], 1, 0)
    df['p_long'] = np.where(df['psar'] < df['Close'], 1, 0)
        
    return df[-3:]

def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()

    for symbol in symbols:
        print(symbol)

        try:
            df = calculate_indicators(symbol, interval=Client.KLINE_INTERVAL_5MINUTE)

            if df is None:
                continue
   
            if df['short'][-2] == 1 and df['p_short'][-2] == 1:
                        
                            message = f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}"
                            Tb.telegram_canal_3por(message)

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

            if df['long'][-2] == 1 and df['p_long'][-2] == 1:
                                               
                            message = f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}"
                            Tb.telegram_canal_3por(message)

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

        except Exception as e:
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)
    run_strategy()
