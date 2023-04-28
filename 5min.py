from binance.client import Client
import pandas as pd
import talib as ta
import Telegram_bot as Tb
import time as ti
import requests
import numpy as np

Pkey = ''
Skey = ''

client = Client(api_key=Pkey, api_secret=Skey)

futures_info = client.futures_exchange_info()

symbols = [
    symbol['symbol'] for symbol in futures_info['symbols']
    if symbol['status'] == "TRADING"
  ]
#symbols = ["BELUSDT", "BNXUSDT", "BTSUSDT", "CELOUSDT","FLMUSDT", "ICXUSDT", "INJUSDT", "IOSTUSDT", "OGNUSDT", "RAYUSDT"]

def indicator(symbol):
      
  kline = client.futures_historical_klines(symbol, "5m", "24 hours ago UTC+1",limit=500)
  df = pd.DataFrame(kline)
  
  if not df.empty:
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    df = df.set_index('Date')
    upperband, middleband, lowerband = ta.BBANDS(df['Close'],
                                               timeperiod=20,
                                               nbdevup=2,
                                               nbdevdn=2,
                                               matype=0)
    Close = float(df['Close'][-2])
   # Calcular la EMA de 200 y 13 períodos y la LRC de 20 períodos
    df['ema_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    df['ema_13'] = df['Close'].ewm(span=13, adjust=False).mean()
    df['lrc'] = ta.LINEARREG(df['Close'], timeperiod=20)

# Encontrar los índices donde la LRC cruza por encima de la EMA y viceversa
    crossover_long = np.where((df['lrc'].shift(1) < df['ema_13'].shift(1)) & (df['lrc'] > df['ema_13']))[0]
    crossover_short = np.where((df['lrc'].shift(1) > df['ema_13'].shift(1)) & (df['lrc'] < df['ema_13']))[0]

# Crear un DataFrame de pandas para almacenar los puntos de cruce
    cross_points = pd.DataFrame(index=df.index, columns=['cross'])

# Asignar 1 a los puntos de cruce alcistas y -1 a los puntos de cruce bajistas
    cross_points.iloc[crossover_long] = 1
    cross_points.iloc[crossover_short] = -1

# Rellenar hacia adelante los valores de cruce para obtener el punto exacto del cruce
    cross_points = cross_points.ffill()

# Agregar la columna de puntos de cruce al DataFrame original
    df['cross'] = cross_points

# Eliminar filas sin cruce
    df.dropna(subset=['cross'], inplace=True)

# Calcular la posición
    df['position'] = df['cross'].diff()
    
        
    info = client.futures_historical_klines("BTCUSDT", "15m", "2 days ago UTC+1",limit=1000) 
    df_new = pd.DataFrame(info)
       
    if not df_new.empty:
        df_new.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close' 'IGNORE',
      'Quote_Volume', 'Trades_Count', 'BUY_VOL', 'BUY_VOL_VAL', 'x']
    df_new['Date'] = pd.to_datetime(df_new['Date'], unit='ms')
    df_new = df_new.set_index('Date')
    cciB = ta.CCI(df_new['High'], df_new['Low'], df_new['Close'], timeperiod=28)
      
           
   # DATOS FNDY
  FISHINGSHORT = {
        "name": "FISHING SHORT",
        "secret": "azsdb9x719",
        "side": "sell",
        "symbol": symbol,
        "open": {
        "price": Close
        }
        }
        
  FISHINGLONG = {
        "name": "FISHING LONG",
        "secret": "0kivpja7tz89",
        "side": "buy",
        "symbol": symbol,
        "open": {
        "price": Close
        }
        }
      
  print(symbol)
      
# TENDENCIA :
  
  if (cciB[-2] > 0):
    if  df['position'][-2] == 1:    
      Tb.telegram_send_message(f"🎣 {symbol}\n🟢 LONG\n⏳ 5 min\n💵 Precio: {Close}\n🎣 Fishing Pisha")
      requests.post('https://hook.finandy.com/OVz7nTomirUoYCLeqFUK', json=FISHINGLONG) 
      
  if (cciB[-2] < 0):       
   if df['position'][-2] == -1: 
      Tb.telegram_send_message(f"🎣 {symbol}\n🔴 SHORT\n⏳ 5 min\n💵 Precio: {Close}\n🎣 Fishing Pisha")
      requests.post('https://hook.finandy.com/q-1NIQZTgB4tzBvSqFUK', json=FISHINGSHORT)   
          

while True:
  current_time = ti.time()
  seconds_to_wait = 300 - current_time % 300
  ti.sleep(seconds_to_wait)   
  
  for symbol in symbols:
      indicator(symbol)
      
