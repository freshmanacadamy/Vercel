from flask import Flask, request
import telebot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        try:
            json_data = request.get_json(force=True)
            bot.process_new_updates([telebot.types.Update.de_json(json_data)])
            return "OK", 200
        except Exception as e:
            print("Error processing update:", e)
            return "Error", 500
    else:  # GET request
        return "🤖 Telegram Bot is Running on Vercel!", 200

# Bot handlers
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "👋 Hello! Send me any image and I’ll forward it to the admin.")

@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    photo_id = message.photo[-1].file_id
    caption = message.caption or "(No caption)"
    bot.send_photo(ADMIN_ID, photo_id,
                   caption=f"From @{message.from_user.username or message.from_user.id}\n\n{caption}")
    bot.reply_to(message, "✅ Image sent to admin!")

@bot.message_handler(func=lambda m: True, content_types=["text"])
def echo_message(message):
    bot.reply_to(message, "📸 Send me an image and I’ll forward it to the admin.")
