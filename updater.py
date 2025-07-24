# updater.py

import os
import subprocess
import time

def log(msg):
    print(f"[UPDATER] {msg}")

try:
    log("🔄 Pulling latest code from GitHub...")
    subprocess.check_call(["git", "pull"])
    log("✅ Code updated successfully.")

    log("📦 Installing/updating dependencies...")
    subprocess.check_call(["pip", "install", "-r", "requirements.txt"])

    log("🔁 Restarting bot...")

    # Kill any running instance of bot.py
    subprocess.call(["pkill", "-f", "bot.py"])
    time.sleep(2)

    # Start bot in background using nohup
    subprocess.Popen(["nohup", "python", "bot.py", "&"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    log("✅ Bot restarted successfully.")

except subprocess.CalledProcessError as e:
    log(f"❌ Update failed: {e}")
except Exception as ex:
    log(f"❌ Unexpected error: {ex}")
