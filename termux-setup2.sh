#!/data/data/com.termux/files/usr/bin/bash

echo "🚀 Starting Telethon Bot Setup in Termux..."

# Step 1: Update Termux
echo "📦 Updating Termux..."
pkg update -y && pkg upgrade -y

# Step 2: Install Required Packages
echo "🔧 Installing required packages..."
pkg install -y git python openssl curl

# Step 3: Clone the Bot Repo
echo "📥 Cloning your bot from GitHub..."
git clone https://github.com/AashooSharma/telethon_vick-bot.git bot
cd bot || { echo "❌ Failed to enter 'bot' folder. Exiting..."; exit 1; }

# Step 4: Install Python Dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 5: Create .env file if not exists
if [ ! -f ".env" ]; then
    echo "🔐 Creating .env file..."
    read -p "Enter your API_ID: " api_id
    read -p "Enter your API_HASH: " api_hash
    read -p "Enter your BOT_TOKEN: " bot_token
    read -p "Enter your OWNER_ID (Telegram User ID): " owner_id

    cat <<EOF > .env
API_ID=$api_id
API_HASH=$api_hash
BOT_TOKEN=$bot_token
OWNER_ID=$owner_id
EOF
else
    echo "✅ .env file already exists. Skipping creation."
fi

# Step 6: Create chat_memory.json if not exists
if [ ! -f "chat_memory.json" ]; then
    echo "{}" > chat_memory.json
    echo "🧠 Initialized empty chat_memory.json"
fi

# Step 7: Create startbot and stopbot shortcuts
echo "⚙️ Creating global startbot and stopbot commands..."

cat <<EOL > $PREFIX/bin/startbot
#!/data/data/com.termux/files/usr/bin/bash
cd ~/bot || exit
nohup python bot.py > bot.log 2>&1 &
echo \$! > bot.pid
echo "✅ Bot started in background!"
EOL

cat <<EOL > $PREFIX/bin/stopbot
#!/data/data/com.termux/files/usr/bin/bash
cd ~/bot || exit
if [ -f bot.pid ]; then
    kill \$(cat bot.pid) && rm bot.pid
    echo "🛑 Bot stopped."
else
    echo "❌ No running bot found."
fi
EOL

chmod +x $PREFIX/bin/startbot
chmod +x $PREFIX/bin/stopbot

# Step 8: Start the bot
echo "🤖 Starting the bot in background..."
nohup python bot.py > bot.log 2>&1 &
echo $! > bot.pid

echo "✅ Bot is running in background!"
echo "📄 View logs with: tail -f bot.log"
echo "▶️ Start again: startbot"
echo "⏹️ Stop bot anytime: stopbot"
