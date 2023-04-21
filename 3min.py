from binance.client import Client
import numpy as np
import pandas as pd
import talib
import Telegram_bot as Tb
import time
import requests


api_key = 'TU_API_KEY'
api_secret = 'TU_API_SECRET'

client = Client(api_key, api_secret)

futures_info = client.futures_exchange_info()
symbols = [symbol['symbol'] for symbol in futures_info['symbols']]

# Crea una función para generar los canales de Fibonacci:
       
#def calculate_adx(prices_high, prices_low, prices):
    #adx = talib.ADX(prices_high, prices_low, prices, timeperiod=14)
    #return adx 

def calculate_indicators(prices_close):
    # Calcula el indicador RSI
    rsi = talib.RSI(prices_close, timeperiod=14)
             
    # Calcula el indicador ADX
    #adx = calculate_adx(prices_high, prices_low, prices_close)
      
    # Calcula Bandas de Bollinger
    upperband, middleband, lowerband = talib.BBANDS(prices_close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=talib.MA_Type.SMA)
    
    return rsi, upperband, middleband, lowerband

def calculate_imbalance(response):
    depth = 20

    bid_sum = sum([float(bid[1]) for bid in response.get('bids', [])])
    ask_sum = sum([float(ask[1]) for ask in response.get('asks', [])])
    
    if bid_sum + ask_sum > 0:
        return (ask_sum - bid_sum) / (bid_sum + ask_sum)
    else:
        return 0.0

def check_symbol(symbol):
    # Obtén los datos de precios históricos para el símbolo
    klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_3MINUTE)
          
    prices_close = np.array([float(kline[5]) for kline in klines])
    
    # Calcula indicadores y bandas de Bollinger
    rsi, upperband, middleband, lowerband = calculate_indicators(prices_close)
    
    #Imbalance
    response = requests.get(f'https://api.binance.com/api/v3/depth?symbol={symbol}&limit=20').json()
    imbalance = calculate_imbalance(response)
        
    diff = abs((np.array([float(kline[3]) for kline in klines]) / np.array([float(kline[4]) for kline in klines]) - 1) * 100)
         
    PORSHORT = {
        "name": "CORTO 3POR",
        "secret": "ao2cgree8fp",
        "side": "sell",
        "symbol": symbol,
        "open": {
            "price": prices_close[-2]
        }
    }
    
    PORLONG = {
        "name": "LARGO 3POR",
        "secret": "nwh2tbpay1r",
        "side": "buy",
        "symbol": symbol,
        "open": {
            "price": prices_close[-2]
        }
    }
    
      
    #Actual   
    if diff[-2] > 1 and prices_close[-2] > upperband[-2] and rsi[-2] > 70 and imbalance < 0.10:
        Tb.telegram_canal_3por(f"⚡️ {symbol}\n🔴 SHORT\n⏳ 3 min \n🔝 Cambio: % {round(diff[-2],2)} \n💵 Precio: {prices_close[-2]}\n IMB: {round(imbalance,2)}") 
        requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORSHORT)
        
    elif diff[-2] > 1 and prices_close[-2] < lowerband[-2] and rsi[-2] < 30 and imbalance > 0.10:
        Tb.telegram_canal_3por(f"⚡️ {symbol}\n🟢 LONG\n⏳ 3 min \n🔝 Cambio: % {round(diff[-2],2)} \n💵 Precio: {prices_close[-2]}\n IMB: {round(imbalance,2)}") 
        requests.post('https://hook.finandy.com/a58wyR0gtrghSupHq1UK', json=PORLONG)

while True:
    for symbol in symbols:
       
        # Espera hasta que sea el comienzo de una nueva hora
        current_time = time.time()
        seconds_to_wait = 180 - current_time % 180
        time.sleep(seconds_to_wait)     
        check_symbol(symbol)
        print(symbol)
    
