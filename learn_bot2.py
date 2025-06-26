import os
import json
from telethon import TelegramClient, events, types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID"))
MEMORY_FILE = "chat_memory.json"

# Load memory from JSON file
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        memory = json.load(f)
else:
    memory = {}

# Save memory to file
def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

# Extract key from a message (text or sticker only)
def get_key_from_message(msg):
    if isinstance(msg.media, types.MessageMediaDocument) and msg.sticker:
        return f"sticker:{msg.file.id}"
    elif msg.message and not msg.media:
        return f"text:{msg.message.strip().lower()}"
    return None

# Extract reply entry (text or sticker only)
def get_entry_from_message(msg):
    if isinstance(msg.media, types.MessageMediaDocument) and msg.sticker:
        return {"type": "sticker", "data": msg.file.id}
    elif msg.message and not msg.media:
        return {"type": "text", "data": msg.message.strip()}
    return None

# Initialize Telegram client (user session)
client = TelegramClient("user_session", API_ID, API_HASH)

# Command: /learn [limit]
@client.on(events.NewMessage(pattern=r"/learn(?: (\d+))?"))
async def learn_command(event):
    if event.sender_id != OWNER_ID:
        return await event.reply("🚫 You are not authorized to use this command.")

    match = event.pattern_match.group(1)
    limit = int(match) if match else 10000

    chat_id = event.chat_id
    progress_msg = await event.reply(f"📚 Learning from last {limit} messages...")

    learned_count = 0
    processed = 0

    async for msg in client.iter_messages(chat_id, limit=limit):
        if msg.is_reply:
            sender = await msg.get_sender()
            if sender and not getattr(sender, "bot", False):
                try:
                    reply_to = await msg.get_reply_message()
                    if not reply_to:
                        continue
                    reply_sender = await reply_to.get_sender()
                    if reply_sender and getattr(reply_sender, "bot", False):
                        continue

                    parent_key = get_key_from_message(reply_to)
                    reply_entry = get_entry_from_message(msg)

                    # Only learn valid (text/sticker ↔ text/sticker)
                    if parent_key and reply_entry:
                        if parent_key not in memory:
                            memory[parent_key] = []

                        if reply_entry not in memory[parent_key]:
                            memory[parent_key].append(reply_entry)
                            learned_count += 1
                except:
                    continue

        processed += 1
        if processed % 500 == 0:
            await progress_msg.edit(
                f"📦 Scanning: {processed}/{limit} messages...\n🧠 Learned replies: {learned_count}"
            )

    save_memory()
    await progress_msg.edit(
        f"✅ Learning complete!\n📘 Processed: {processed}\n🧠 New replies learned: {learned_count}"
    )

# Start client
print("🤖 Learn bot is running... Use /learn inside any group.")
client.start()
client.run_until_disconnected()
    
