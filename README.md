# 🤖 Telethon Vick-Bot

A smart and memory-enabled Telegram bot built using [Telethon](https://github.com/LonamiWebs/Telethon).  
This bot **learns from message and sticker replies**, stores them in a local JSON database, and automatically replies with random responses it has learned — just like a mini AI bot!

---

## ✨ Features

- ✅ `/start`, `/help` — Basic usage info
- ✅ `/update` — Pull latest code from GitHub (admin only)
- ✅ `/remove_msg` — Delete a message and all its replies from memory (admin only)
- ✅ `/remove_reply` — Delete a specific reply to a message (admin only)
- ✅ 💬 Learns from text and sticker replies
- ✅ 🧠 Replies automatically to known messages or stickers
- ✅ 🎲 Picks a random response if multiple are stored
- ✅ ✅ Termux-compatible installer

---

## 🧠 How It Works

1. If a user **replies** to a message or sticker with **text or sticker**, the bot saves it.
2. Next time someone sends that message or sticker, the bot will randomly reply using a stored reply.
3. Supports infinite learning and self-improvement via conversation!

---

## 🔐 .env Configuration

Create a `.env` file in the project directory:

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
OWNER_ID=your_telegram_user_id
````

Use [@userinfobot](https://t.me/userinfobot) to get your `OWNER_ID`.

---

## 🛠 Installation

### ✅ Regular Setup (Linux/PC)

```bash
git clone https://github.com/AashooSharma/telethon_vick-bot.git
cd telethon_vick-bot
bash setup.sh
```

---

### 📱 Termux Setup

```bash
pkg install wget -y
wget https://raw.githubusercontent.com/AashooSharma/telethon_vick-bot/main/termux-setup.sh
chmod +x termux-setup.sh
./termux-setup.sh
```

---

## 📂 Project Structure

```
telethon_vick-bot/
├── bot.py               # Main bot logic
├── updater.py           # Pull updates from GitHub & restart bot
├── chat_memory.json     # Learned messages & sticker replies (auto-generated)
├── .env                 # API credentials (not tracked by Git)
├── requirements.txt     # Required Python libraries
├── setup.sh             # Linux install script
└── termux-setup.sh      # Full auto-setup for Termux users
```

---

## 🔧 Admin Commands

| Command         | Description                                                      |
| --------------- | ---------------------------------------------------------------- |
| `/update`       | Pull latest code and restart (owner only)                        |
| `/remove_msg`   | Delete message and all replies (reply to target message)         |
| `/remove_reply` | Delete specific reply (reply to message and type the reply text) |

---

## 📈 Future Features (Optional)

* 💾 Migrate memory to MongoDB / SQLite
* 🔄 Button-based feedback to rate replies
* 🧠 NLP-powered response suggestions
* 📊 Analytics for most triggered messages

---

## 🤝 Author & Credits

* 💻 Created by [Aashoo Sharma](https://aashoosharma.tech)
* 🧠 Built using [Telethon](https://github.com/LonamiWebs/Telethon)
* 📦 Python-based AI memory system

---

## 📜 License

This project is open-source under the **MIT License**.
Feel free to fork, improve, and contribute! ❤️

