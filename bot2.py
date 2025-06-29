import os
import json
import random
import subprocess
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

def get_key_from_message(msg):
    if msg.sticker:
        return f"sticker:{msg.file.id}"
    elif msg.message:
        return f"text:{msg.message.strip().lower()}"
    return None

def get_key_from_event(event):
    if event.message.sticker:
        return f"sticker:{event.message.file.id}"
    elif event.message.message:
        return f"text:{event.message.message.strip().lower()}"
    return None

# Initialize bot
bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# /start command
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    sender = await event.get_sender()
    await event.respond(
        f"👋 Hello {sender.first_name}!\n\n"
        "I'm your memory-based Telegram bot!\n"
        "Type /help for instructions."
    )

# /help command
@bot.on(events.NewMessage(pattern="/help"))
async def help_cmd(event):
    await event.respond(
        "**📚 Bot Help**\n\n"
        "🔹 Reply to a message/sticker with text or sticker → I’ll learn it\n"
        "🔹 I’ll reply randomly when I’ve learned multiple replies\n"
        "🔸 **Commands:**\n"
        "`/update` – Pull latest code (owner only)\n"
        "`/remove_msg` – Delete full message from memory (reply to msg)\n"
        "`/remove_reply` – Delete specific reply (reply + type text to remove)\n"
        "`/database` – Show memory statistics"
    )

# /update command (admin only)
@bot.on(events.NewMessage(pattern="/update"))
async def update(event):
    if event.sender_id != OWNER_ID:
        return await event.respond("🚫 You are not authorized to update the bot.")
    await event.respond("🔄 Pulling latest code and restarting...")
    subprocess.Popen(["python3", "updater.py"])

# /database command
@bot.on(events.NewMessage(pattern="/database"))
async def database(event):
    if event.sender_id != OWNER_ID:
        return await event.respond("🚫 You are not authorized to use this command.")

    total_keys = len(memory)
    total_replies = 0
    text_replies = 0
    sticker_replies = 0

    for replies in memory.values():
        total_replies += len(replies)
        for r in replies:
            if r["type"] == "text":
                text_replies += 1
            elif r["type"] == "sticker":
                sticker_replies += 1

    msg = (
        "📊 **Database Stats:**\n"
        f"🧠 Learned Messages: `{total_keys}`\n"
        f"💬 Total Replies: `{total_replies}`\n"
        f"✏️ Text Replies: `{text_replies}`\n"
        f"🎉 Sticker Replies: `{sticker_replies}`"
    )
    await event.respond(msg)

# /remove_msg command
@bot.on(events.NewMessage(pattern="/remove_msg"))
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
        await event.respond("❌ Message not found in memory.")

# /remove_reply command
@bot.on(events.NewMessage(pattern="/remove_reply"))
async def remove_reply(event):
    if event.sender_id != OWNER_ID or not event.is_reply:
        return await event.respond("❌ Reply to the message and type the reply to remove.")
    msg = await event.get_reply_message()
    reply_text = event.message.message.strip().lower()
    key = get_key_from_message(msg)
    if not key or key not in memory:
        return await event.respond("❌ Original message not found in memory.")

    original_len = len(memory[key])
    memory[key] = [
        x for x in memory[key]
        if not (x["type"] == "text" and x["data"].strip().lower() == reply_text)
    ]
    if len(memory[key]) < original_len:
        if not memory[key]:
            del memory[key]
        save_memory()
        await event.respond("✅ Reply removed.")
    else:
        await event.respond("❌ Reply not found.")


@bot.on(events.NewMessage(pattern="/backup"))
async def backup(event):
    if event.sender_id != OWNER_ID:
        return await event.respond("❌ You are not authorized to use this command.")

    try:
        if os.path.exists(MEMORY_FILE):
            confirm_msg = await event.respond("📤 Sending database file to owner...")
            await bot.send_file(
                OWNER_ID,
                MEMORY_FILE,
                caption="🧠 *Bot Memory Backup File*\nHere is the latest `chat_memory.json`.",
                force_document=True
            )
            await confirm_msg.edit("✅ Backup sent to owner.")
        else:
            await event.respond("⚠️ No database file found to backup.")
    except Exception as e:
        error_msg = f"❌ Failed to send backup: `{str(e)}`"
        await event.respond(error_msg)
        await bot.send_message(OWNER_ID, f"❌ Backup error: {str(e)}")

# @bot.on(events.NewMessage(pattern="/backup"))
# async def backup(event):
#     if event.sender_id != OWNER_ID:
#         return await event.respond("❌ You are not authorized to use this command.")

#     if os.path.exists(MEMORY_FILE):
#         await bot.send_file(OWNER_ID, MEMORY_FILE, caption="🧠 Bot database backup file")
#     else:
#         await event.respond("⚠️ No database file found.")

# /cmd command (run termux command and send output)
@bot.on(events.NewMessage(pattern=r"^/cmd (.+)"))
async def cmd_terminal(event):
    if event.sender_id != OWNER_ID:
        return await event.respond("❌ You're not authorized to run shell commands.")
    
    command = event.pattern_match.group(1)
    output_file = "output.txt"

    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=15, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        result = e.output
    except subprocess.TimeoutExpired:
        result = "⏱️ Command timed out."

    # Write result to file
    with open(output_file, "w") as f:
        f.write(result if result else "✅ Command ran with no output.")

    await bot.send_file(event.chat_id, output_file, caption=f"📁 Output of:\n`{command}`", force_document=True)
    os.remove(output_file)


# Learn and respond logic
@bot.on(events.NewMessage)
async def handle_message(event):
    if event.out:
        return

    key = get_key_from_event(event)

    # Learn reply
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        parent_key = get_key_from_message(replied_msg)
        if parent_key:
            if parent_key not in memory:
                memory[parent_key] = []

            if event.message.sticker:
                entry = {"type": "sticker", "data": event.message.file.id}
            elif event.message.message:
                entry = {"type": "text", "data": event.message.message.strip()}
            else:
                return

            if entry not in memory[parent_key]:
                memory[parent_key].append(entry)
                save_memory()

    # Reply to known message/sticker
    if key and key in memory:
        reply = random.choice(memory[key])
        if reply["type"] == "text":
            await event.respond(reply["data"], reply_to=event.message.id)
        elif reply["type"] == "sticker":
            await bot.send_file(event.chat_id, reply["data"], reply_to=event.message.id)

# Start bot
print("✅ Bot is running... Waiting for messages.")
bot.run_until_disconnected()
