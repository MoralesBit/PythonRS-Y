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

def calculate_order_block(df):
    # Calcular el tamaño del order block
    df['range'] = df['High'] - df['Low']
    order_block_range = df['range'].quantile(0.2)
    df['order_block'] = (df['High'] - df['Low']) <= order_block_range
    
    # Calcular los puntos con mayor acumulación
    df['accumulation'] = ta.AD(df['High'], df['Low'], df['Close'], df['Volume'])
    accumulation_threshold = df['accumulation'].quantile(0.8)
    df['high_accumulation'] = df['accumulation'] >= accumulation_threshold
    
    # Calcular el punto de acumulación más bajo
    lowest_accumulation = df['accumulation'].min()
    df['low_accumulation'] = df['accumulation'] == lowest_accumulation
    
    return df

def get_trading_symbols():
    """Obtiene la lista de símbolos de futuros de Binance que están disponibles para trading"""
    futures_info = client.futures_exchange_info()
    symbols = [symbol['symbol'] for symbol in futures_info['symbols'] if symbol['status'] == "TRADING"]
    #symbols = ["IMXUSDT","LEVERUSDT","ACHUSDT","AGLDUSDT"]
    coins_to_remove = ["ETHBTC", "USDCUSDT", "BNBBTC", "ETHUSDT", "BTCDOMUSDT","XMRUSDT", "BTCUSDT_230929","XEMUSDT","BLUEBIRDUSDT","ETHUSDT_231229","DOGEUSDT","LITUSDT","ETHUSDT_230929","BTCUSDT_231229","ETCUSDT"]  # Lista de monedas a eliminar
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
    df[['Open', 'High', 'Low', 'Close','Volume']] = df[['Open', 'High', 'Low', 'Close','Volume']].astype(float)
    
    rsi = ta.RSI(df['Close'], timeperiod=14)
    df['rsi'] = rsi
    
    slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], 14, 14, 0, 3)
    df['slowk'] = slowk
    df['slowd'] = slowd
    
    df['sl_short'] = np.where(df['slowk'][-3] > df['slowd'][-3] and df['slowk'][-2] <= df['slowd'][-2],1,0)
    df['sl_long'] = np.where(df['slowk'][-3] < df['slowd'][-3] and df['slowk'][-2] >= df['slowd'][-2],1,0)
    
    df['rsi_short'] = np.where(df['rsi'][-3] < 30 and df['rsi'][-2] >= 30,1,0)
    df['rsi_long'] = np.where(df['rsi'][-3] > 70 and df['rsi'][-2] <= 70,1,0)
    
                              
    return df[-3:]
        
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
                           
        print(symbol)
        
        try:
           
            df = calculate_indicators(symbol)
            dfr = calculate_order_block(df)
            short = df['Close'][-2]*(0.9999)
            long = df['Close'][-2]*(0.001) + df['Close'][-2]
            
            dfr['acu_symbol'] = np.where(df['high_accumulation'][-2] == True ,"🟢","🔴")
                       
            print(dfr['high_accumulation'][-2])
            print(dfr['low_accumulation'][-2])
            print(dfr['order_block'][-2])
            print(dfr['acu_symbol'] [-2])
                                             
            if df is None:
                continue
            #Contratendencia:
            
            if dfr['low_accumulation'][-2] == True and df['rsi'][-2] > 70:
                if df['sl_short'][-2] == 1:    
                    
                    Tb.telegram_canal_3por(f"🔴 {symbol} \n💵 Precio: {df['Close'][-2]}\n💲 HA: {df['acu_symbol'][-2]}\n⏳ 5 Minutos")
                    PICKERSHORT = {
                            "name": "PICKER SHORT",
                            "secret": "ao2cgree8fp",
                            "side": "sell",
                            "symbol": symbol,
                            "open": {
                            "price": short 
                            }
                            }
   
                    requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PICKERSHORT)                         
                    
                    
            if dfr['low_accumulation'][-2] == True and df['rsi'][-2] < 30:
                if df['sl_long'][-2] == 1:
                
                    Tb.telegram_canal_3por(f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}\n💲 HA: {df['acu_symbol'][-2]}\n⏳ 5 Minutos")
                    PICKERLONG = {
                            "name": "PICKER LONG",
                            "secret": "nwh2tbpay1r",
                            "side": "buy",
                            "symbol": symbol,
                            "open": {
                            "price": long
                            }
                            }
                    requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PICKERLONG)
            
            #Tendencia:        
            if dfr['high_accumulation'][-2] == True and dfr['order_block'][-2] == True and  df['rsi_long'][-2] == 1:
                    
                    Tb.telegram_send_message(f"🟢 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}\n⏳ 5 Minutos")
                    
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
                    
                    
            if dfr['high_accumulation'][-2] == True and dfr['order_block'][-2] == True and df['rsi_short'][-2] == 1:
                    
                    Tb.telegram_send_message(f"🔴 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}\n⏳ 5 Minutos")
                    
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

        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
