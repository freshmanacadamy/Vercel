import os
import telebot
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Store user data in memory (volatile - resets on redeploy)
user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_data[user_id] = {'step': 'main'}
    
    bot.reply_to(message, 
        "🤖 *Welcome to Simple Bot!*\n\n"
        "Available commands:\n"
        "/start - Show this message\n"
        "/echo - Echo your text\n" 
        "/info - Show your info\n"
        "/image - Forward image to admin\n\n"
        "Built for Vercel 🚀",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['echo'])
def echo_text(message):
    user_id = message.from_user.id
    user_data[user_id] = {'step': 'waiting_echo'}
    
    bot.reply_to(message, "📝 Send me any text and I'll echo it back!")

@bot.message_handler(commands=['info'])
def show_info(message):
    user = message.from_user
    info_text = f"""
👤 *Your Info:*
🆔 ID: `{user.id}`
📛 Name: {user.first_name} {user.last_name or ''}
🔗 Username: @{user.username or 'None'}
🌐 Language: {user.language_code or 'Unknown'}
    """
    bot.reply_to(message, info_text, parse_mode='Markdown')

@bot.message_handler(commands=['image'])
def request_image(message):
    user_id = message.from_user.id
    user_data[user_id] = {'step': 'waiting_image'}
    
    bot.reply_to(message, "📸 Send me an image and I'll forward it to admin!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    
    if user_data.get(user_id, {}).get('step') == 'waiting_image':
        try:
            # Forward to admin
            photo_id = message.photo[-1].file_id
            caption = f"From: @{message.from_user.username or message.from_user.id}"
            
            if ADMIN_ID:
                bot.send_photo(ADMIN_ID, photo_id, caption=caption)
                bot.reply_to(message, "✅ Image sent to admin!")
            else:
                bot.reply_to(message, "✅ Image received! (Admin not configured)")
                
            user_data[user_id] = {'step': 'main'}
            
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")
    else:
        bot.reply_to(message, "📸 Nice photo! Use /image to send to admin.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    user_state = user_data.get(user_id, {})
    
    if user_state.get('step') == 'waiting_echo':
        bot.reply_to(message, f"🔁 Echo: {message.text}")
        user_data[user_id] = {'step': 'main'}
    else:
        bot.reply_to(message, 
            "❓ Unknown command. Use:\n"
            "/start - Show help\n"
            "/echo - Echo text\n" 
            "/info - Your info\n"
            "/image - Send image to admin"
        )

# Vercel serverless handler
@app.route("/api/bot", methods=["POST", "GET"])
def webhook():
    if request.method == "POST":
        try:
            json_data = request.get_json()
            update = telebot.types.Update.de_json(json_data)
            bot.process_new_updates([update])
        except Exception as e:
            print("Error:", e)
        return "OK"
    else:
        return "🤖 Telegram Bot is running on Vercel! Use POST for webhook."

# Set webhook (run once)
def set_webhook():
    import requests
    webhook_url = f"https://{os.getenv('VERCEL_URL')}/api/bot"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    print(f"Webhook set to: {webhook_url}")

# For local testing
if __name__ == "__main__":
    if os.getenv("VERCEL") is None:  # Running locally
        print("🤖 Polling mode (local)...")
        bot.remove_webhook()
        bot.polling()
    else:  # Running on Vercel
        set_webhook()
