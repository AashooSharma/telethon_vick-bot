import os
import json
from telethon import TelegramClient, events
from dotenv import load_dotenv

# Load env variables
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
MEMORY_FILE = "chat_memory.json"

# Load memory
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        memory = json.load(f)
else:
    memory = {}

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def get_key_from_message(msg):
    if msg.sticker:
        return f"sticker:{msg.file.id}"
    elif msg.message:
        return f"text:{msg.message.strip().lower()}"
    return None

def get_entry_from_message(msg):
    if msg.sticker:
        return {"type": "sticker", "data": msg.file.id}
    elif msg.message:
        return {"type": "text", "data": msg.message.strip()}
    return None

# Init bot
bot = TelegramClient("bot_learn", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern="/learn"))
async def learn_from_chat(event):
    if event.sender_id != OWNER_ID:
        return await event.respond("🚫 You are not authorized to use /learn.")
    
    await event.respond("📚 Scanning messages and learning replies... This may take a while.")
    
    chat_id = event.chat_id
    learned_count = 0
    processed = 0

    async for msg in bot.iter_messages(chat_id, limit=10000):
        if msg.is_reply and not msg.from_id.bot:
            try:
                reply_to = await msg.get_reply_message()
                if not reply_to or reply_to.from_id.bot:
                    continue

                parent_key = get_key_from_message(reply_to)
                reply_entry = get_entry_from_message(msg)

                if parent_key and reply_entry:
                    if parent_key not in memory:
                        memory[parent_key] = []

                    if reply_entry not in memory[parent_key]:
                        memory[parent_key].append(reply_entry)
                        learned_count += 1

            except:
                continue

        processed += 1
        if processed % 1000 == 0:
            print(f"Processed: {processed}, Learned: {learned_count}")

    save_memory()
    await event.respond(f"✅ Learned {learned_count} new replies from chat history.")

print("📘 Learn bot is running... Use /learn in chat.")
bot.run_until_disconnected()
