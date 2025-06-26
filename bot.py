import os
import subprocess
import json
import random
from telethon import TelegramClient, events
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
MEMORY_FILE = "chat_memory.json"

# Load or initialize memory
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        memory = json.load(f)
else:
    memory = {}

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def get_key_from_event(event):
    if event.message.sticker:
        return f"sticker:{event.message.file.id}"
    elif event.message.message:
        return f"text:{event.message.message.strip().lower()}"
    return None

def get_key_from_message(msg):
    if msg.sticker:
        return f"sticker:{msg.file.id}"
    elif msg.message:
        return f"text:{msg.message.strip().lower()}"
    return None

# Init bot
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await event.get_sender()
    await event.respond(
        f"👋 Hello {sender.first_name}!\n\n"
        "I am your helpful Telethon Bot.\n"
        "Type /help to see how I work!"
    )

@bot.on(events.NewMessage(pattern='/help'))
async def help_command(event):
    await event.respond(
        "📖 *Bot Usage Guide:*\n\n"
        "✅ /start – Intro\n"
        "✅ /help – Show help\n"
        "✅ /update – Pull latest from GitHub\n"
        "✅ /remove_msg – Delete message & replies\n"
        "✅ /remove_reply – Delete specific reply\n"
        "🧠 Reply to messages or stickers with text/stickers – I’ll remember!"
    )

@bot.on(events.NewMessage(pattern='/update'))
async def update_command(event):
    if event.sender_id != OWNER_ID:
        return await event.respond("🚫 Not authorized.")
    await event.respond("🔄 Updating bot...")
    subprocess.Popen(["python3", "updater.py"])

@bot.on(events.NewMessage(pattern='/remove_msg'))
async def remove_msg(event):
    if event.sender_id != OWNER_ID or not event.is_reply:
        return await event.respond("❌ Reply to the message/sticker you want to remove.")
    msg = await event.get_reply_message()
    key = get_key_from_message(msg)
    if key and key in memory:
        del memory[key]
        save_memory()
        await event.respond(f"🗑️ Removed all replies for: `{key}`")
    else:
        await event.respond("❌ Not found in memory.")

@bot.on(events.NewMessage(pattern='/remove_reply'))
async def remove_reply(event):
    if event.sender_id != OWNER_ID or not event.is_reply:
        return await event.respond("❌ Reply to the original message, and type the exact reply to remove.")
    replied = await event.get_reply_message()
    key = get_key_from_message(replied)
    if not key or key not in memory:
        return await event.respond("❌ Original not found.")
    
    target_text = event.message.message.strip().lower() if event.message.message else None
    if not target_text:
        return await event.respond("❌ Text reply to remove must be provided.")

    original_len = len(memory[key])
    memory[key] = [x for x in memory[key] if not (x["type"] == "text" and x["data"].strip().lower() == target_text)]

    if len(memory[key]) < original_len:
        if not memory[key]: del memory[key]
        save_memory()
        await event.respond("✅ Reply removed.")
    else:
        await event.respond("❌ Reply not found.")

# Main learning & reply logic
@bot.on(events.NewMessage)
async def learn_and_reply(event):
    sender_id = event.sender_id
    key = get_key_from_event(event)

    # ✅ LEARN if it's a reply
    if event.is_reply:
        replied = await event.get_reply_message()
        parent_key = get_key_from_message(replied)
        if not parent_key:
            return

        if parent_key not in memory:
            memory[parent_key] = []

        # Save reply (text or sticker)
        if event.message.sticker:
            new_entry = {"type": "sticker", "data": event.message.file.id}
        elif event.message.message:
            new_entry = {"type": "text", "data": event.message.message.strip()}
        else:
            return

        if new_entry not in memory[parent_key]:
            memory[parent_key].append(new_entry)
            save_memory()

    # ✅ RESPOND if message/sticker is already stored
    if key and key in memory:
        reply = random.choice(memory[key])
        if reply["type"] == "text":
            await event.respond(reply["data"])
        elif reply["type"] == "sticker":
            await bot.send_file(event.chat_id, reply["data"])
