import os
import telebot
from flask import Flask, request
import google.genai as genai

# Токени
TOKEN = os.getenv("8328585321:AAFoNYLKLvX_lHxf91qcPb8Fdj0Uw608zvI")
GEMINI_KEY = os.getenv("AIzaSyC8nMCdo2SQn2HrpVxkt7T0_PjSPexZhW0")

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(name)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return 'OK', 200
    return '<h1>Бот працює!</h1>', 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not message.text:
        return
        
    status_msg = bot.reply_to(message, "🎨 Зачекайте, Nano Banana малює...")
    
    try:
        # Створюємо клієнт прямо тут
        client = genai.Client(api_key=GEMINI_KEY)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[message.text]
        )
        
        # Шукаємо картинку в частинах відповіді
        found_image = False
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    bot.send_photo(message.chat.id, part.inline_data.data)
                    bot.delete_message(message.chat.id, status_msg.message_id)
                    found_image = True
                    break
        
        if not found_image:
            bot.edit_message_text("❌ ШІ не надіслав зображення. Спробуйте інший опис.", message.chat.id, status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Помилка: {str(e)}", message.chat.id, status_msg.message_id)

# Обов'язково для Vercel
def handler(request):
    return app(request)
