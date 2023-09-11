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
    
    df['rsi'] = ta.RSI(df['Close'], timeperiod=14)
    df['sma'] = ta.SMA(df['rsi'], timeperiod=20)
    df['sma_signal'] = np.where(df['sma'] < 50, 1, 0)
    
    df['ema200'] = df['Close'].ewm(span=200, adjust=False).mean()
    df['ema22'] = df['Close'].ewm(span=22, adjust=False).mean()
    
    df['cross_down'] = np.where(df['Close'][-3] > df['ema22'][-3] and  df['Close'][-2] < df['ema22'][-2] and df['ema200'][-2] > df['ema22'][-2], 1, 0)
    df['cross_up'] = np.where(df['Close'][-3] < df['ema22'][-3] and  df['Close'][-2] > df['ema22'][-2] and df['ema200'][-2] < df['ema22'][-2], 1, 0)
    
   
    #df['ema_long'] = np.where(df['Close'] > df['ema22'] > df['ema200'] , 1, 0)
    #df['ema_short'] = np.where(df['Close'] > df['ema22'] > df['ema200'] , 1, 0)

    acceleration=0.02
    maximum=1

    df['psar'] = ta.SAR(df['High'], df['Low'], acceleration, maximum)

    df['p_short'] = np.where(df['psar'] > df['Close'], 1, 0)
    df['p_long'] = np.where(df['psar'] < df['Close'], 1, 0)
    
    df['p_cross_short'] = np.where(df['psar'][-3] < df['Close'][-3] and df['psar'][-2] > df['Close'][-2], 1, 0)
    df['p_cross_long'] = np.where(df['psar'][-3] > df['Close'][-3] and df['psar'][-2] < df['Close'][-2], 1, 0)
    
    df['cci'] = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=28)
    df['cci_signal'] = np.where(df['cci'][-2] > 0,1,0)

    return df[-3:]


def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
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
    
    df['rsi'] = ta.RSI(df['Close'], timeperiod=14)
    df['sma'] = ta.SMA(df['rsi'], timeperiod=20)
    df['sma_signal'] = np.where(df['sma'] < 50, 1, 0)
    
    df['ema200'] = df['Close'].ewm(span=200, adjust=False).mean()
    df['ema22'] = df['Close'].ewm(span=22, adjust=False).mean()
    
    df['cross_down'] = np.where(df['Close'][-3] > df['ema22'][-3] and  df['Close'][-2] < df['ema22'][-2] and df['ema200'][-2] > df['ema22'][-2], 1, 0)
    df['cross_up'] = np.where(df['Close'][-3] < df['ema22'][-3] and  df['Close'][-2] > df['ema22'][-2] and df['ema200'][-2] < df['ema22'][-2], 1, 0)
    
   
    #df['ema_long'] = np.where(df['Close'] > df['ema22'] > df['ema200'] , 1, 0)
    #df['ema_short'] = np.where(df['Close'] > df['ema22'] > df['ema200'] , 1, 0)

    acceleration=0.02
    maximum=1

    df['psar'] = ta.SAR(df['High'], df['Low'], acceleration, maximum)

    df['p_short'] = np.where(df['psar'] > df['Close'], 1, 0)
    df['p_long'] = np.where(df['psar'] < df['Close'], 1, 0)
    
    df['p_cross_short'] = np.where(df['psar'][-3] < df['Close'][-3] and df['psar'][-2] > df['Close'][-2], 1, 0)
    df['p_cross_long'] = np.where(df['psar'][-3] > df['Close'][-3] and df['psar'][-2] < df['Close'][-2], 1, 0)
    
    df['cci'] = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=28)
    df['cci_signal'] = np.where(df['cci'][-2] > 0,1,0)

    return df[-3:]


def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
    sent_message = False
    
    for symbol in symbols:
        print(symbol)

        try:
            df = calculate_indicators(symbol, interval=Client.KLINE_INTERVAL_5MINUTE)
            df_btc = calculate_indicators("BTCUSDT", interval=Client.KLINE_INTERVAL_5MINUTE)

            if df is None:
                continue
            
            
            
            if df_btc['p_cross_short'][-2] == 1 and not sent_message:
                message = f"Cierran los LONG"
                Tb.telegram_canal_prueba(message)
                CLOSELONG= {
                "name": "CLOSE LONG",
                "secret": "luj6ewrkwje",
                "side": "buy",
                "symbol": symbol
                }
                requests.post('https://hook.finandy.com/p-0RG59xlYnRP-A-qVUK', json=CLOSELONG)
                sent_message = True
                
            if df_btc['p_cross_long'][-2] == 1 and not sent_message:
                message = f"Cierran los SHORT"
                Tb.telegram_canal_prueba(message)
                CLOSESHORT= {
                "name": "CLOSE LONG",
                "secret": "5vzf98rzhrf",
                "side": "buy",
                "symbol": symbol
                }
                requests.post('https://hook.finandy.com/B5IDjcrXh2P_5OE-qVUK', json=CLOSESHORT)
                sent_message = True
                
            if df_btc['p_short'][-2] == 1:
                if df['cross_down'][-2] == 1:
                    if df['p_short'][-2] == 1 and df['cci_signal'][-2] == 0:      
                        if df['sma_signal'][-2] == 1:
                        
                            message = f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}"
                            Tb.telegram_send_message(message)

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

            if df_btc['p_long'][-2] == 1:
                if df['cross_up'][-2] == 1:
                    if df['p_long'][-2] == 1 and df['cci_signal'][-2] == 1:    
                        if df['sma_signal'][-2] == 0: 
                                               
                            message = f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}"
                            Tb.telegram_send_message(message)

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

            else:
                print("NEXT")
                
            
            
        except Exception as e:
            print(f"Error en el símbolo {symbol}: {e}")


while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)
    run_strategy()
    
    # VERSION ESTABLE
    for symbol in symbols:
        print(symbol)

        try:
            df = calculate_indicators(symbol, interval=Client.KLINE_INTERVAL_5MINUTE)
            df_btc = calculate_indicators("BTCUSDT", interval=Client.KLINE_INTERVAL_5MINUTE)

            if df is None:
                continue
            
            
            
            if df_btc['p_cross_short'][-2] == 1 and not sent_message:
                message = f"Cierran los LONG"
                Tb.telegram_canal_prueba(message)
                CLOSELONG= {
                "name": "CLOSE LONG",
                "secret": "luj6ewrkwje",
                "side": "buy",
                "symbol": symbol
                }
                requests.post('https://hook.finandy.com/p-0RG59xlYnRP-A-qVUK', json=CLOSELONG)
                sent_message = True
                
            if df_btc['p_cross_long'][-2] == 1 and not sent_message:
                message = f"Cierran los SHORT"
                Tb.telegram_canal_prueba(message)
                CLOSESHORT= {
                "name": "CLOSE LONG",
                "secret": "5vzf98rzhrf",
                "side": "buy",
                "symbol": symbol
                }
                requests.post('https://hook.finandy.com/B5IDjcrXh2P_5OE-qVUK', json=CLOSESHORT)
                sent_message = True
                
            if df_btc['p_short'][-2] == 1:
                if df['cross_down'][-2] == 1:
                    if df['p_short'][-2] == 1 and df['cci_signal'][-2] == 0:      
                        if df['sma_signal'][-2] == 1:
                        
                            message = f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}"
                            Tb.telegram_send_message(message)

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

            if df_btc['p_long'][-2] == 1:
                if df['cross_up'][-2] == 1:
                    if df['p_long'][-2] == 1 and df['cci_signal'][-2] == 1:    
                        if df['sma_signal'][-2] == 0: 
                                               
                            message = f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}"
                            Tb.telegram_send_message(message)

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

            else:
                print("NEXT")
                
            sent_message = False
            
        except Exception as e:
            print(f"Error en el símbolo {symbol}: {e}")


while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)
    run_strategy()
    
    # VERSION ESTABLE
