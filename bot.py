import os
import json
from dotenv import load_dotenv
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Load file .env
load_dotenv()

# Ambil variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
MINIAPP_URL = os.getenv('MINIAPP_URL')
ADMIN_ID = os.getenv('ADMIN_ID')  # Tambahkan ini di .env

# File untuk simpan user IDs
USERS_FILE = 'users.json'

def load_users():
    """Load daftar user dari file"""
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_user(user_id):
    """Simpan user ID baru"""
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
        print(f"✅ New user saved: {user_id}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Simpan user ID
    save_user(user_id)
    
    # Debug: cek URL yang kebaca
    print(f"DEBUG - URL yang dipakai: {MINIAPP_URL}")
    
    if not MINIAPP_URL or MINIAPP_URL == "https://your-miniapp-url.com":
        await update.message.reply_text("❌ MINIAPP_URL belum diset di file .env!")
        return
    
    # Buat tombol
    keyboard = [[
        InlineKeyboardButton(
            text="COLLECT WOOT", 
            web_app=WebAppInfo(url=MINIAPP_URL)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Hi.. Welcome 👋🏻\nClaim WOOT by farming easily now\nAnd collect limited rewards for you! 🎉",
        reply_markup=reply_markup
    )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command untuk broadcast pesan ke semua user (admin only)"""
    user_id = update.effective_user.id
    
    # Cek apakah user adalah admin
    if ADMIN_ID and str(user_id) != ADMIN_ID:
        await update.message.reply_text("❌ You do not have access to broadcast!")
        return
    
    # Cek apakah ada pesan yang mau di-broadcast
    if not context.args:
        await update.message.reply_text(
            "📢 Cara pakai:\n/broadcast <pesan kamu>\n\n"
            "Contoh:\n/broadcast 🎁 WOOT tokens ready to collect!"
        )
        return
    
    # Gabungkan semua argumen jadi satu pesan
    message = ' '.join(context.args)
    
    # Load semua user
    users = load_users()
    
    if not users:
        await update.message.reply_text("❌ There are no registered users yet!")
        return
    
    # Kirim ke semua user
    success = 0
    failed = 0
    
    await update.message.reply_text(f"📤 Sending broadcast to {len(users)} user...")
    
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            success += 1
        except Exception as e:
            print(f"❌ Failed sending to {user_id}: {e}")
            failed += 1
    
    await update.message.reply_text(
        f"✅ Broadcast done!\n\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to check the number of users"""
    user_id = update.effective_user.id
    
    # Cek apakah user adalah admin
    if ADMIN_ID and str(user_id) != ADMIN_ID:
        await update.message.reply_text("❌ You don't have access to stats!")
        return
    
    users = load_users()
    await update.message.reply_text(f"📊 Total users: {len(users)}")

def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set yet!")
        return
    
    print(f"✅ Bot token: {BOT_TOKEN[:10]}...")
    print(
