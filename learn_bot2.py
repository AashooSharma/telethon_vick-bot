import os
import json
from telethon import TelegramClient, events, types
from dotenv import load_dotenv

# Load .env
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID"))  # Only this user can use /learn
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
    if isinstance(msg.media, types.MessageMediaDocument) and msg.file:
        return f"sticker:{msg.file.id}"
    elif msg.message:
        return f"text:{msg.message.strip().lower()}"
    return None

def get_entry_from_message(msg):
    if isinstance(msg.media, types.MessageMediaDocument) and msg.file:
        return {"type": "sticker", "data": msg.file.id}
    elif msg.message:
        return {"type": "text", "data": msg.message.strip()}
    return None

client = TelegramClient("user_session", API_ID, API_HASH)

@client.on(events.NewMessage(pattern="/learn"))
async def learn_command(event):
    if event.sender_id != OWNER_ID:
        return await event.reply("🚫 You are not authorized to use this command.")

    chat_id = event.chat_id
    await event.reply("📚 Learning from last 10,000 messages in this group...")

    learned_count = 0
    processed = 0

    async for msg in client.iter_messages(chat_id, limit=10000):
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
    await event.reply(f"✅ Learning complete. New replies added: `{learned_count}`")

print("🤖 Learn bot is running (user login)...")
client.start()
client.run_until_disconnected()
