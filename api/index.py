import os
import telebot
from flask import Flask, request
from google import genai

# Отримання ключів
TOKEN = os.environ.get('8328585321:AAFoNYLKLvX_lHxf91qcPb8Fdj0Uw608zvI')
GEMINI_KEY = os.environ.get('AIzaSyC8nMCdo2SQn2HrpVxkt7T0_PjSPexZhW0')

app = Flask(name)

# Ініціалізація бота
bot = None
if TOKEN:
    bot = telebot.TeleBot(TOKEN, threaded=False)

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        if not bot: return "Бот не ініціалізований", 500
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    
    # Сторінка для перевірки статусу в браузері
    t_status = "✅ OK" if TOKEN else "❌ Відсутній"
    g_status = "✅ OK" if GEMINI_KEY else "❌ Відсутній"
    return f"<h1>Статус бота:</h1><p>Telegram: {t_status}</p><p>Gemini: {g_status}</p>", 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not message.text or not GEMINI_KEY: return
    
    msg = bot.reply_to(message, "🍌 Малюю ваш запит...")
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[message.text]
        )
        
        found = False
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                bot.send_photo(message.chat.id, part.inline_data.data)
                bot.delete_message(message.chat.id, msg.message_id)
                found = True
                break
        if not found:
            bot.edit_message_text("ШІ не зміг створити фото.", message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"Помилка: {str(e)}", message.chat.id, msg.message_id)

def handler(request):
    return app(request)
