import time
import logging
import threading
import numpy as np
import pandas as pd
import ccxt
from datetime import datetime
import requests
import http.client
import urllib.parse
import json

# ⚙️ Configuración del bot
INTERVALO = "1m"
INTERVALO_SEGUNDOS = 60  # 1 minuto
SIMBOLO = "NEIROETHUSDT"  # Formato correcto para CCXT

# 📬 Configuración Finandy - LONG
FINANDY_LONG_WEBHOOK_URL = "https://hook.finandy.com/AD0_DiCNFu5ej6_NrlUK"
FINANDY_LONG_WEBHOOK_SECRET = "nyd4fj2qgp"
FINANDY_LONG_TRIGGER_NAME = "SR_Alert_LONG"

# 📬 Configuración Finandy - SHORT
FINANDY_SHORT_WEBHOOK_URL = "https://hook.finandy.com/tUiWJBz7dKN4RKLNrlUK"
FINANDY_SHORT_WEBHOOK_SECRET = "i35k43dxwx"
FINANDY_SHORT_TRIGGER_NAME = "SR_Alert_SHORT"

# 📊 Configuración Indicadores
PERIODO_ATR = 14
PERIODO_STOCH = 14
SOBRECOMPRA = 80
SOBREVENTA = 20

def enviar_telegram(mensaje):
    """Envía un mensaje a Telegram."""
    TELEGRAM_TOKEN = "5028180661:AAHM9j4jxsU_bCLpxbNjOtP5DIAT_UgUs-s"  # Reemplaza con tu token de Telegram
    TELEGRAM_CHAT_ID = "-1001760455133"  # Reemplaza con tu chat ID de Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"✅ Mensaje enviado a Telegram: {mensaje}")
        else:
            print(f"❌ Error enviando mensaje a Telegram: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Excepción enviando mensaje a Telegram: {e}")

# 🧠 Función para calcular ATR
def calcular_atr(df, periodo=14):
    df['H-L'] = df['high'] - df['low']
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(periodo).mean()
    return df['ATR']

# 🧠 Función para calcular Estocástico
def calcular_estocastico(df, periodo=14):
    df['min_14'] = df['low'].rolling(periodo).min()
    df['max_14'] = df['high'].rolling(periodo).max()
    df['stoch_k'] = 100 * (df['close'] - df['min_14']) / (df['max_14'] - df['min_14'])
    df['stoch_d'] = df['stoch_k'].rolling(3).mean()
    return df['stoch_k'], df['stoch_d']

# 📡 Enviar alerta a Finandy
def send_finandy_webhook(symbol, side):
    if side == "buy":
        if not FINANDY_LONG_WEBHOOK_URL or FINANDY_LONG_WEBHOOK_URL == "TU_FINANDY_LONG_WEBHOOK_URL":
            logging.warning(f"Webhook LONG de Finandy no configurado para {symbol}. Saltando envío.")
            return
        webhook_url = FINANDY_LONG_WEBHOOK_URL
        payload = {
            "name": FINANDY_LONG_TRIGGER_NAME,
            "secret": FINANDY_LONG_WEBHOOK_SECRET,
            "side": "buy",
            "symbol": SIMBOLO,
            "comment": f"Alerta 1m: Posible rebote/continuacion alcista basado en {INTERVALO}."
        }
    elif side == "sell":
        if not FINANDY_SHORT_WEBHOOK_URL or FINANDY_SHORT_WEBHOOK_URL == "TU_FINANDY_SHORT_WEBHOOK_URL":
            logging.warning(f"Webhook SHORT de Finandy no configurado para {symbol}. Saltando envío.")
            return
        webhook_url = FINANDY_SHORT_WEBHOOK_URL
        payload = {
            "name": FINANDY_SHORT_TRIGGER_NAME,
            "secret": FINANDY_SHORT_WEBHOOK_SECRET,
            "side": "sell",
            "symbol": SIMBOLO,
            "comment": f"Alerta 1m: Posible retroceso/continuacion bajista basado en {INTERVALO}."
        }
    else:
        logging.warning(f"Side '{side}' inválido para {symbol}")
        return

    try:
        url_parsed = urllib.parse.urlparse(webhook_url)
        conn = http.client.HTTPSConnection(url_parsed.netloc)
        headers = {"Content-Type": "application/json"}
        json_data = json.dumps(payload)

        conn.request("POST", url_parsed.path, body=json_data, headers=headers)
        response = conn.getresponse()
        response_data = response.read().decode()
        print(f"✅ Alerta enviada a Finandy ({side}) → {symbol} | Status: {response.status} | Respuesta: {response_data}")
        conn.close()
    except Exception as e:
        logging.error(f"❌ Error enviando alerta a Finandy para {symbol} → {e}")

# 🔄 Obtener datos del mercado
def obtener_datos():
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(SIMBOLO, INTERVALO, limit=100)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# 🔍 Analizar datos y generar señales
def analizar_y_generar_senales():
    df = obtener_datos()

    # Calcular indicadores
    df['ATR'] = calcular_atr(df, PERIODO_ATR)
    df['ATR_SMA'] = df['ATR'].rolling(14).mean()
    df['stoch_k'], df['stoch_d'] = calcular_estocastico(df, PERIODO_STOCH)

    # Señales
    condicion_long = (
        (df['stoch_k'].iloc[-2] < SOBREVENTA) &
        (df['stoch_k'].iloc[-1] > SOBREVENTA) &
        (df['ATR'].iloc[-1] > df['ATR_SMA'].iloc[-1])
    )
    condicion_short = (
        (df['stoch_k'].iloc[-2] > SOBRECOMPRA) &
        (df['stoch_k'].iloc[-1] < SOBRECOMPRA) &
        (df['ATR'].iloc[-1] > df['ATR_SMA'].iloc[-1])
    )

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if condicion_long:
        mensaje = f"{ahora} | 🟢 {SIMBOLO}"
        
        print(mensaje)
        send_finandy_webhook(SIMBOLO, "buy")
        enviar_telegram(mensaje)

    elif condicion_short:
        mensaje = f"{ahora} | 🔴 {SIMBOLO}"
        print(mensaje)
        #send_finandy_webhook(SIMBOLO, "sell")
        #enviar_telegram(mensaje)

    print(f"[+] Análisis completado para {SIMBOLO} a las {ahora}")

# 🕒 Loop principal del bot
def ejecutar_bot():
    while True:
        try:
            analizar_y_generar_senales()
        except Exception as e:
            print(f"[!] Error durante la ejecución: {e}")
        time.sleep(INTERVALO_SEGUNDOS)

# 🚀 Iniciar bot
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("[+] Bot de Trading iniciado...")
    hilo_principal = threading.Thread(target=ejecutar_bot)
    hilo_principal.start()