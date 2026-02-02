import os
from flask import Flask, request
import telebot
from google import genai

# Отримання ключів
TOKEN = os.environ.get('8328585321:AAFoNYLKLvX_lHxf91qcPb8Fdj0Uw608zvI')
API_KEY = os.environ.get('AIzaSyC8nMCdo2SQn2HrpVxkt7T0_PjSPexZhW0')

# Ініціалізація
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(name)

@app.route('/', methods=['GET', 'POST'])
def handle_webhook():
    if request.method == 'POST':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return '<h1>Nano Banana Bot is Live!</h1>', 200

@bot.message_handler(func=lambda message: True)
def on_message(message):
    if not message.text:
        return
        
    prompt = message.text
    temp_msg = bot.reply_to(message, "🍌 Nano Banana малює... зачекайте")
    
    try:
        # Ініціалізація клієнта всередині функції (це надійніше для Vercel)
        client = genai.Client(api_key=API_KEY)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        
        # Перевірка наявності зображення
        found = False
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    bot.send_photo(message.chat.id, part.inline_data.data)
                    bot.delete_message(message.chat.id, temp_msg.message_id)
                    found = True
                    break
        
        if not found:
            bot.edit_message_text("❌ ШІ не надіслав зображення. Спробуй інший промпт.", message.chat.id, temp_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Помилка: {str(e)}", message.chat.id, temp_msg.message_id)

# Обов'язково для Vercel Runtime
def handler(request):
    return app(request)
