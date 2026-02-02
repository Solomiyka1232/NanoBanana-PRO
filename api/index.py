import os
import telebot
from flask import Flask, request
from google import genai

# Налаштування
TOKEN = os.getenv("8328585321:AAFoNYLKLvX_lHxf91qcPb8Fdj0Uw608zvI")
API_KEY = os.getenv("AIzaSyC8nMCdo2SQn2HrpVxkt7T0_PjSPexZhW0")

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(name)

# Спробуємо ініціалізувати Gemini
def get_client():
    return genai.Client(api_key=API_KEY)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return 'OK', 200
    return '<h1>Бот онлайн!</h1>', 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not message.text:
        return
        
    wait_msg = bot.reply_to(message, "🎨 Малюю ваш запит через Nano Banana...")
    
    try:
        client = get_client()
        # Використовуємо модель 2.0 Flash
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[message.text]
        )
        
        found = False
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    bot.send_photo(message.chat.id, part.inline_data.data)
                    bot.delete_message(message.chat.id, wait_msg.message_id)
                    found = True
                    break
        
        if not found:
            bot.edit_message_text("ШІ не зміг згенерувати картинку. Спробуйте інший опис.", message.chat.id, wait_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Помилка: {str(e)}", message.chat.id, wait_msg.message_id)

# Це важливо для Vercel Python Runtime
def handler(request):
    return app(request)
