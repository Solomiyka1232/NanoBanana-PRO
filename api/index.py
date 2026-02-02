import os
import telebot
from flask import Flask, request
import google.genai as genai

# Отримуємо змінні
TOKEN = os.environ.get('8328585321:AAFoNYLKLvX_lHxf91qcPb8Fdj0Uw608zvI')
GEMINI_KEY = os.environ.get('AIzaSyC8nMCdo2SQn2HrpVxkt7T0_PjSPexZhW0')

app = Flask(name)

# Створюємо об'єкт бота тільки якщо є токен
bot = None
if TOKEN:
    bot = telebot.TeleBot(TOKEN, threaded=False)

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if not TOKEN:
        return "Помилка: TELEGRAM_TOKEN не знайдено в системі!", 500
        
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    return "<h1>Бот онлайн і чекає на Webhook!</h1>", 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not message.text: return
    
    status_msg = bot.reply_to(message, "🎨 Nano Banana малює...")
    
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[message.text]
        )
        
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                bot.send_photo(message.chat.id, part.inline_data.data)
                bot.delete_message(message.chat.id, status_msg.message_id)
                return
        
        bot.edit_message_text("❌ Не вдалося згенерувати фото.", message.chat.id, status_msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Помилка: {str(e)}", message.chat.id, status_msg.message_id)

def handler(request):
    return app(request)
