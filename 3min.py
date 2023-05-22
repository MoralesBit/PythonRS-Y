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
    
    df[['Open', 'High', 'Low', 'Close']] = df[['Open', 'High', 'Low', 'Close']].astype(float)
    
    diff = abs((df['High'] / df['Low'] -1) * 100)
    
    df['diff'] = diff
         
    rsi = ta.RSI(df['Close'], timeperiod=14)
    df['rsi'] = rsi 
           
    ema_3 = df['Close'].ewm(span=3, adjust=False).mean()
    df['ema_3'] = ema_3
    
    roc = ta.ROC(df['Close'], timeperiod=6)
    df['roc'] = roc
      
    
    # Obtener el libro de órdenes actual
    order_book = client.get_order_book(symbol=symbol)
        
    # Obtener el sentimiento del mercado
    total_bid_amount = sum([float(bid[1]) for bid in order_book['bids']])
    total_ask_amount = sum([float(ask[1]) for ask in order_book['asks']])
    market_sentiment = (total_bid_amount - total_ask_amount) / (total_bid_amount + total_ask_amount)
    df['market_sentiment'] = market_sentiment
    
    # Obtener la posible dirección del precio
    bid_prices = np.array([float(bid[0]) for bid in order_book['bids']])
    ask_prices = np.array([float(ask[0]) for ask in order_book['asks']])
    bid_volumes = np.array([float(bid[1]) for bid in order_book['bids']])
    ask_volumes = np.array([float(ask[1]) for ask in order_book['asks']])
    bid_cumulative_volumes = np.cumsum(bid_volumes)
    ask_cumulative_volumes = np.cumsum(ask_volumes)

    bid_support = np.where(bid_cumulative_volumes > np.max(bid_cumulative_volumes)*0.15)[0][0]
    ask_resistance = np.where(ask_cumulative_volumes > np.max(ask_cumulative_volumes)*0.15)[0][0]

    df['bid_support'] = bid_prices[bid_support]
    df['ask_resistance'] = ask_prices[ask_resistance] 
      
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
            upperband, middleband, lowerband = ta.BBANDS(df['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
           
            if df is None:
                continue
            # CONTRATENDENCIAs:         
             
            if (df['diff'][-3] >= 1) and (df['ema_3'][-2] <= float(df['Close'][-2])):
                if (df['rsi'][-3] > df['rsi'][-2]):
                       
                    Tb.telegram_send_message(f"🔴 {symbol} ▫️ {round(df['market_sentiment'][-2],2)}\n💵 Precio: {df['Close'][-2]}\n📍 Picker ▫️ 3 min")
                    
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

                
            if (df['diff'][-3] >= 1) and (df['ema_3'][-2] >= float(df['Close'][-2])) :    
                 if (df['rsi'][-3] < df['rsi'][-2]):  
                    Tb.telegram_send_message(f"🟢 {symbol} ▫️ {round(df['market_sentiment'][-2],2)}\n💵 Precio: {df['Close'][-2]}\n📍 Picker ▫️ 3 min")
                                
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
    
                
        except Exception as e:
          
            print(f"Error en el símbolo {symbol}: {e}")

while True:
    current_time = time.time()
    seconds_to_wait = 180 - current_time % 180
    time.sleep(seconds_to_wait)    
    run_strategy()
