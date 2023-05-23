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
    
    ema_3 = df['Close'].ewm(span=3, adjust=False).mean()
    df['ema_3'] = ema_3
            
    rsi = ta.RSI(df['Close'], timeperiod=14)
    df['rsi'] = rsi 
       
    roc = ta.ROC(df['Close'], timeperiod=6)
    df['roc'] = roc
      
    slowk, slowd = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    df['slowk'] = slowk
    df['slowd'] = slowd  
    
    # Obtener el libro de órdenes actual
    order_book = client.get_order_book(symbol=symbol)
        
    # Obtener el sentimiento del mercado
    total_bid_amount = sum([float(bid[1]) for bid in order_book['bids']])
    total_ask_amount = sum([float(ask[1]) for ask in order_book['asks']])
    market_sentiment = (total_bid_amount - total_ask_amount) / (total_bid_amount + total_ask_amount)
    df['market_sentiment'] = market_sentiment
            
    # Calcula el agotamiento de precio
            
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
       
    diff = abs((df['High'] / df['Low'] -1) * 100)
    
    df['diff'] = diff   
    
    return df[-3:]
    
def get_last_funding_rate(symbol):
    try:
        # Obtener el historial de tasas de financiamiento
        funding_history = client.futures_funding_rate(symbol=symbol)

        # Obtener la última tasa de financiamiento
        ff = None
        for funding_info in funding_history:
            ff = float(funding_info['fundingRate']) * 100
        # Devolver la última tasa de financiamiento
        return ff

    except Exception as e:
        print(f"Error en el símbolo {symbol}: {e}")
        return None
    
def run_strategy():
    """Ejecuta la estrategia de trading para cada símbolo en la lista de trading"""
    symbols = get_trading_symbols()
       
    for symbol in symbols:
        ff = get_last_funding_rate(symbol)
               
        print(symbol)
                                       
        try:
            df = calculate_indicators(symbol)
            
                             
            if df is None:
                continue
            # CONTRATENDENCIAs:         
             
            if (df['diff'][-3] >= 1) and ((df['Close'][-3]) >= df['upperband'][-3]):
                
                if  df['slowk'][-1] < df['slowd'][-1]: 
                       
                    Tb.telegram_canal_3por(f"🔴 {symbol} ▫️ {round(df['market_sentiment'][-2],2)}\n💵 Precio: {df['Close'][-2]}\n📍 Picker ▫️ 3 min")
                    
                    PORSHORT = {
                    "name": "CORTO 3POR",
                    "secret": "ao2cgree8fp",
                    "side": "sell",
                    "symbol": symbol,
                    "open": {
                    "price": float(df['Close'][-2]) 
                    }
                    }
   
                    requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT)    

                
            if (df['diff'][-3] >= 1) and ((df['Close'][-3]) <= df['lowerband'][-3]): 
                   
                if  df['slowk'][-1] > df['slowd'][-1]:  
                    
                    Tb.telegram_canal_3por(f"🟢 {symbol} ▫️ {round(df['market_sentiment'][-2],2)}\n💵 Precio: {df['Close'][-2]}\n📍 Picker ▫️ 3 min")
                                
                    PORLONG = {
                    "name": "LARGO 3POR",
                    "secret": "nwh2tbpay1r",
                    "side": "buy",
                    "symbol": symbol,
                    "open": {
                    "price": float(df['Close'][-2]) 
                    }
                    }
                    requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG) 
            
            
            #TENDENCIA:
            
            if (df['diff'][-2] >= 1) and ((df['Close'][-2]) >= df['upperband'][-2]):
                    
                if  float(df['bid_orders'][-2]) >  float(df['ask_orders'][-2]): 
                    
                    Tb.telegram_canal_prueba(f"🟢 {symbol} ▫️ {round(df['market_sentiment'][-2],2)}\n💵 Precio: {df['Close'][-2]}\n📍 Trend ▫️ 3 min")     
                                       
                 
                    requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT)    

                
            if (df['diff'][-2] >= 1) and ((df['Close'][-2]) <= df['lowerband'][-2]) and (df['d_up'][-2] > 0.5):    
               
                if  float(df['bid_orders'][-2]) <  float(df['ask_orders'][-2]):
                         
                    Tb.telegram_canal_prueba(f"🔴 {symbol} ▫️ {round(df['market_sentiment'][-2],2)}\n💵 Precio: {df['Close'][-2]}\n📍 Trend ▫️ 3 min")
                       
            
                    requests.post('https://hook.finandy.com/o5nDpYb88zNOU5RHq1UK', json=PORLONG) 
      
    
                
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 180 - current_time % 180
    time.sleep(seconds_to_wait)    
    run_strategy()
