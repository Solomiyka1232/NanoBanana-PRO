import os
import telebot
from flask import Flask, request
from google import genai

# Змінні з налаштувань Vercel
TOKEN = os.getenv("8328585321:AAFoNYLKLvX_lHxf91qcPb8Fdj0Uw608zvI")
GEMINI_KEY = os.getenv("AIzaSyC8nMCdo2SQn2HrpVxkt7T0_PjSPexZhW0")

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(name)

# Створення клієнта Gemini
client = genai.Client(api_key=GEMINI_KEY)

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200
    return "Бот працює!", 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    prompt = message.text
    status = bot.reply_to(message, "🎨 Малюю... зачекайте")
    
    try:
        # Використовуємо актуальну модель Nano Banana
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=[prompt]
        )
        
        # Шукаємо картинку в результаті
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                bot.send_photo(message.chat.id, part.inline_data.data)
                bot.delete_message(message.chat.id, status.message_id)
                return
        
        bot.edit_message_text("ШІ не зміг створити фото за цим описом.", message.chat.id, status.message_id)
    except Exception as e:
        bot.edit_message_text(f"Помилка: {str(e)}", message.chat.id, status.message_id)

if name == "main":
    app.run()
