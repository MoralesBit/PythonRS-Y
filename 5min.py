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
   
def calculate_indicators(symbol,interval):
        
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=1000)
    df = pd.DataFrame(klines)
    if df.empty:
        return None
    df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                  'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    
    df = df.set_index('Open time')
           
    df[['Open', 'High', 'Low', 'Close','Volume']] = df[['Open', 'High', 'Low', 'Close','Volume']].astype(float) 
     
    df['ema200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    acceleration=0.02 
    maximum=0.20
    
    df['psar'] = ta.SAR(df['High'], df['Low'], acceleration, maximum)
    
    df['p_short'] = np.where( df['psar'][-2] < df['Close'][-2] and df['psar'][-1] > df['Close'][-1],1,0) 
    df['p_long'] = np.where( df['psar'][-2] > df['Close'][-2] and df['psar'][-1] < df['Close'][-1],1,0)
    df['top_short'] = np.where( df['psar'] > df['Close'],1,0)
    df['down_long'] = np.where( df['psar'] < df['Close'],1,0)  
        
    df['ema_short'] = np.where( df['ema200'] > df['Close'],1,0)
    df['ema_long'] = np.where( df['ema200'] < df['Close'],1,0)
    
    df['roc'] = ta.ROC(df['Close'], timeperiod=288)
    
    df['roc_long'] = np.where(df['roc'][-2] > 10,1,0)
    df['roc_short'] = np.where( df['roc'][-2] < -10,1,0)
    
    df['diff'] = abs((df['Close'] / df['psar'] -1) * 100)
    df['diff_signal'] = np.where(df['diff'] >= 3,1,0)

    df['Volume'] = pd.to_numeric(df['Volume'])
    df['Close'] = pd.to_numeric(df['Close'])
    #Calcular el oscilador de volumen en porcentaje usando las longitudes corta y larga:
    df['Short Avg'] = df['Volume'].rolling(5).mean()
    df['Long Avg'] = df['Volume'].rolling(10).mean()
    df['Volume_Oscillator'] = ((df['Short Avg'] - df['Long Avg']) / df['Long Avg']) * 100
    df['vol_positivo'] = np.where(df['Volume_Oscillator'] >= 5,1,0)
    df['vol_negativo'] = np.where(df['Volume_Oscillator'] <= -5,1,0)
    df['vol_max'] = np.where(df['Volume_Oscillator'] >= 45,1,0)
    df['vol_min'] = np.where(df['Volume_Oscillator'] <= -45,1,0)
    df['v_cross_down'] = np.where(df['Volume_Oscillator'][-2] > -20 and df['Volume_Oscillator'][-2] <= -20 ,1,0)
    df['v_cross_up'] = np.where(df['Volume_Oscillator'][-2] < 20 and df['Volume_Oscillator'][-2] >= 20 ,1,0)
         
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
           
            if df['vol_positivo'][-1] == 1 and df['p_long'][-1] == 1:
                    if df['ema_long'][-1] == 1:
                        if df['roc_long'][-1] == 1:  
                            
                                message = f"🟢 {symbol} \n💵 Precio: {df['Close'][-2]}"
                                Tb.telegram_send_message(message)
                                              
                                Tendencia_Long = {
                                "name": "FISHING LONG",
                                "secret": "0kivpja7tz89",
                                "side": "buy",
                                "symbol": symbol,
                                "open": {
                                "price": float(df['Close'][-2])
                                }
                                 }
                                requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=Tendencia_Long)
            
            if df['top_short'][-1] == 1:
                if df['v_cross_down'][-1] ==1:
                    if df['ema_long'][-1] == 1:
                        if df['roc_long'][-1] == 1: 
                            Tb.telegram_canal_prueba(f"🟢 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}")
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
                                                     
            if df['vol_positivo'][-1] == 1 and df['p_short'][-1] == 1 :
                    if df['ema_short'][-1] == 1:
                        if df['roc_short'][-1] == 1:   

                            message = f"🔴 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}"
                            Tb.telegram_send_message(message)
                                  
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
            
            if df['v_cross_up'][-1] == 1:
                if  df['down_long'][-1] == 1:
                    if df['ema_short'][-1] == 1:
                        if df['roc_short'][-1] == 1:  
                            
                            Tb.telegram_canal_prueba(f"🔴 {symbol} \n💵 Precio: {round(df['Close'][-1],4)}")
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

        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 300 - current_time % 300
    time.sleep(seconds_to_wait)    
    run_strategy()
    #VERSION ESTABLE
