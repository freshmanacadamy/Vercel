from flask import Flask, request
import telebot
import os

# ============================
# CONFIGURATION
# ============================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Add this in Vercel Environment Variables
ADMIN_ID = os.getenv("ADMIN_ID")    # Your Telegram user ID (add this too)
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ============================
# ROUTES
# ============================
@app.route("/", methods=["POST"])
def webhook():
    json_data = request.get_json(force=True)
    bot.process_new_updates([telebot.types.Update.de_json(json_data)])
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "🤖 Telegram Bot is Running on Vercel!", 200


# ============================
# BOT HANDLERS
# ============================

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "👋 Hello! Send me any image and I’ll forward it to the admin.")


# 🖼 Receive image and send to admin
@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    try:
        # Get the highest-quality photo file ID
        photo_id = message.photo[-1].file_id
        caption = message.caption or "(No caption)"

        # Notify user
        bot.reply_to(message, "📤 Image received! Sending to admin...")

        # Forward image to admin
        bot.send_photo(ADMIN_ID, photo_id, caption=f"From @{message.from_user.username or message.from_user.id}\n\n{caption}")

        # Confirm success
        bot.reply_to(message, "✅ Image sent to admin!")
    except Exception as e:
        bot.reply_to(message, f"❌ Error sending image: {e}")


# ✉️ Handle text messages normally
@bot.message_handler(func=lambda m: True, content_types=["text"])
def echo_message(message):
    bot.reply_to(message, "📸 Send me an image and I’ll forward it to the admin.")


# ============================
# ENTRY POINT
# ============================
# Do not use bot.polling() here — Vercel uses webhooks