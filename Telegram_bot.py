import requests

def telegram_send_message(message):
    bot_token = "5028180661:AAHM9j4jxsU_bCLpxbNjOtP5DIAT_UgUs-s"
    bot_chatID = "-1001760455133"
    send_text = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+bot_chatID+"&parse_mode=Markdown&text="+message
    response = requests.get(send_text)
    return response.json()

def telegram_canal_prueba(message):
    bot_token = "5028180661:AAHM9j4jxsU_bCLpxbNjOtP5DIAT_UgUs-s"
    bot_chatID = "-1001721640586"
    send_text = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+bot_chatID+"&parse_mode=Markdown&text="+message
    response = requests.get(send_text)
    return response.json()

def telegram_canal_3por(message):
    bot_token = "5028180661:AAHM9j4jxsU_bCLpxbNjOtP5DIAT_UgUs-s"
    bot_chatID = "-1001780906332"
    send_text = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+bot_chatID+"&parse_mode=Markdown&text="+message
    response = requests.get(send_text)
    return response.json()
