import os
import telebot
from flask import Flask, request
from google import genai

# Твій токен та ключ
TOKEN = '8328585321:AAFoNYLKLvX_lHxf91qcPb8Fdj0Uw608zvI'
# Ключ Gemini краще брати з налаштувань, але якщо хочеш, впиши замість os.environ.get
GEMINI_KEY = os.environ.get('AIzaSyC8nMCdo2SQn2HrpVxkt7T0_PjSPexZhW0')

# ОПЕЧАТКА БУЛА ТУТ: має бути __name__
app = Flask(__name__)

# Ініціалізація бота
bot = telebot.TeleBot(TOKEN, threaded=False)

@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        try:
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
        except Exception as e:
            print(f"Помилка вебхука: {e}")
        return "OK", 200
    
    # Сторінка перевірки
    g_status = "✅ OK" if GEMINI_KEY else "❌ Відсутній ключ Gemini у налаштуваннях Vercel"
    return f"<h1>Nano Banana працює!</h1><p>Статус Gemini: {g_status}</p>", 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not message.text or not GEMINI_KEY:
        return

    msg = bot.reply_to(message, "🍌 Малюю...")
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[message.text]
        )
        
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                bot.send_photo(message.chat.id, part.inline_data.data)
                bot.delete_message(message.chat.id, msg.message_id)
                return
        bot.edit_message_text("Не вдалося створити картинку.", message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"Помилка: {str(e)}", message.chat.id, msg.message_id)

# Обробник для Vercel
def handler(request):
    return app(request)
