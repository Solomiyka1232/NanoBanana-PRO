import os
import telebot
from flask import Flask, request
from google import genai

# Ініціалізація
TOKEN = os.getenv("8328585321:AAFoNYLKLvX_lHxf91qcPb8Fdj0Uw608zvI")
GEMINI_KEY = os.getenv("AIzaSyC8nMCdo2SQn2HrpVxkt7T0_PjSPexZhW0")

bot = telebot.TeleBot(TOKEN, threaded=False)
client = genai.Client(api_key=GEMINI_KEY)
app = Flask(name)

@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Forbidden', 403

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    prompt = message.text
    sent_msg = bot.reply_to(message, "🎨 Малюю...")
    
    try:
        # Виклик моделі
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt]
        )
        
        # Відправка фото
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                bot.send_photo(message.chat.id, part.inline_data.data)
                bot.delete_message(message.chat.id, sent_msg.message_id)
    except Exception as e:
        bot.reply_to(message, f"Помилка: {str(e)}")

# Vercel потребує 'app'
