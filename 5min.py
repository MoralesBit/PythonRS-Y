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
    klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_5MINUTE, limit=1000)
    df = pd.DataFrame(klines)
    if df.empty:
        return None
    df.columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                  'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    
    df = df.set_index('Open time')
    
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
      
    rsi = ta.RSI(df['Close'], timeperiod=14)
    df['rsi'] = rsi 
    
    adx= ta.ADX(df['High'], df['Low'], df['Close'], timeperiod=14)
    df['adx'] = adx
    
    ema_50 = df['Close'].ewm(span=50, adjust=False).mean()
    df['ema_50'] = ema_50
    
    roc = ta.ROC(df['Close'], timeperiod=6)
    df['roc'] = roc
    
    cci = ta.CCI(df['High'], df['Low'], df['Close'], timeperiod=58)
    df['cci'] = cci
    
    # Obtener el libro de órdenes actual
    order_book = client.get_order_book(symbol=symbol)

        
    # Obtener el sentimiento del mercado
    total_bid_amount = sum([float(bid[1]) for bid in order_book['bids']])
    total_ask_amount = sum([float(ask[1]) for ask in order_book['asks']])
    market_sentiment = (total_bid_amount - total_ask_amount) / (total_bid_amount + total_ask_amount)
    df['market_sentiment'] = market_sentiment
    
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
          
             
            if df['market_sentiment'][-2] < -0.3:                         
             if (df['rsi'][-3] > 71) and (df['rsi'][-2] <= 69) and (df['adx'][-3] < df['adx'][-2]) :  
 
              Tb.telegram_canal_3por(f"🔴 {symbol} ({round(ff,3)}) ▫️ {round(df['market_sentiment'][-2],2)}\n💵 Precio: {df['Close'][-2]}\n📍 Picker ▫️ 5 min")
            
              PICKERSHORT= {
                "name": "PICKER SHORT",
                "secret": "hgw3399vhh",
                "side": "sell",
                "symbol": symbol,
                "open": {
                "price": float(df['Close'][-1])
                }
                }
   
              requests.post('https://hook.finandy.com/30oL3Xd_SYGJzzdoqFUK', json=PICKERSHORT)    
         
            
            if df['market_sentiment'][-2] > 0.3:  
            
             if (df['rsi'][-3] < 19) and (df['rsi'][-2] >= 21) and (df['adx'][-3] < df['adx'][-2]):    
               
              Tb.telegram_canal_3por(f"🟢 {symbol} ({round(ff,3)}) ▫️ {round(df['market_sentiment'][-2],2)}\n💵 Precio: {df['Close'][-2]}\n📍 Picker ▫️ 5 min") 
            
              PICKERLONG = {
               "name": "PICKER LONG",
               "secret": "xjth0i3qgb",
               "side": "buy",
               "symbol": symbol,
               "open": {
               "price": float(df['Close'][-2]) 
              }
              }
              requests.post('https://hook.finandy.com/lIpZBtogs11vC6p5qFUK', json=PICKERLONG) 
            
            #FISHING PISHA:
           
                
            if df['market_sentiment'][-2] < -0.3:                         
             if (df['rsi'][-3] > 51) and (df['rsi'][-2] <= 49) and (df['adx'][-3] < df['adx'][-2]) :   
                 
                Tb.telegram_send_message(f"🔴 {symbol} ({round(ff,3)}) - {round(df['market_sentiment'][-2],2)}\n💵 Precio: {df['Close'][-2]}\n🎣 Fishing Pisha ▫️ 5 min") 
            
                FISHINGSHORT = {
                "name": "FISHING SHORT",
                "secret": "azsdb9x719",
                "side": "sell",
                "symbol": symbol,
                "open": {
                "price": float(df['Close'][-1])
                }
                }
                requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT) 
            
              
                
            if df['market_sentiment'][-2] > 0.3:  
            
              if (df['rsi'][-3] < 49) and (df['rsi'][-2] >= 51) and (df['adx'][-3] < df['adx'][-2]):  
                   
                Tb.telegram_send_message(f"🟢 {symbol} ({round(ff,3)}) - {round(df['market_sentiment'][-2],2)}\n💵 Precio: {df['Close'][-2]}\n🎣 Fishing Pisha ▫️ 5 min")            
              
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
