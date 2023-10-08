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
    #symbols = ["IMXUSDT","LEVERUSDT","ACHUSDT","AGLDUSDT"]
    coins_to_remove = ["ETHBTC", "USDCUSDT", "BNBBTC", "ETHUSDT", "BTCDOMUSDT", "BTCUSDT_230929","XEMUSDT","BLUEBIRDUSDT","ETHUSDT_231229","DOGEUSDT","LITUSDT","ETHUSDT_230929","BTCUSDT_231229","ETCUSDT"]  # Lista de monedas a eliminar
    for coin in coins_to_remove:
        if coin in symbols:
            symbols.remove(coin)
    return symbols
   
def calculate_indicators(symbol):
        
    klines = client.futures_klines(symbol=symbol,interval=Client.KLINE_INTERVAL_5MINUTE, limit=1000)
    df = pd.DataFrame(klines)
    if df.empty:
        return None
    df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                  'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    
    df = df.set_index('Open time')
    
    df['upper_band'], df['middle_band'], df['lower_band'] = ta.BBANDS(df['Close'], timeperiod=20, nbdevup=3.5, nbdevdn=3.5, matype=0)
    df['slowk'], df['slowd'] = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=14, slowk_matype=0, slowd_period=3, slowd_matype=0)
       
    df[['Open', 'High', 'Low', 'Close','Volume']] = df[['Open', 'High', 'Low', 'Close','Volume']].astype(float) 
   
    df['diff_up'] = abs((df['High'] / df['upper_band'] -1) * 100)
    df['diff_down'] = abs((df['Low'] / df['lower_band'] -1) * 100)
  
    df['rsi'] = ta.RSI(df['Close'], timeperiod=14)
               
    return df
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
        
        try:
           
            df = calculate_indicators(symbol)
                                                                        
            if df is None:
                continue
            
            if df['middle_band'][-2] >= df['Close'][-2]:
                if df['slowk'][-3] <= df['slowd'][-3] and  df['slowk'][-2] >= df['slowd'][-2] < 15:
                   
                        Tb.telegram_canal_3por(f"🟢 {symbol} \n💵 Precio: {round(df['Close'][-1],4)} 📊 {round(df['diff_down'][-1],2)}%")
                        contratendencia_long = {
                            "name": "PICKER LONG",
                            "secret": "nwh2tbpay1r",
                            "side": "buy",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-2])
                            }
                            }
                        requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=contratendencia_long)   

            if df['middle_band'][-2] <= df['Close'][-2]:
                if df['slowk'][-3] >= df['slowd'][-3] and  df['slowk'][-2] <= df['slowd'][-2] > 85:
                                                  
                        Tb.telegram_canal_3por(f"🔴 {symbol} \n💵 Precio: {round(df['Close'][-1],4)} 📊 {round(df['diff_up'][-1],2)}%")
                        contratendencia_short = {
                            "name": "PICKER SHORT",
                            "secret": "ao2cgree8fp",
                            "side": "sell",
                            "symbol": symbol,
                            "open": {
                            "price": float(df['Close'][-1])
                            }
                            }
                        requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=contratendencia_short)

        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
