import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# ─────────────────────────
# Flask Web Server (Required for Render Free Web Service)
# ─────────────────────────

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# Start Flask in background thread
Thread(target=run_web).start()


# ─────────────────────────
# Discord Bot Setup
# ─────────────────────────

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    async def setup_hook(self):
        # Load all cogs
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")

bot = MyBot(
    command_prefix=".",
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ─────────────────────────
# Start Bot
# ─────────────────────────

token = os.getenv("TOKEN")

if not token:
    print("❌ TOKEN NOT FOUND in environment variables.")
else:
    print("✅ TOKEN LOADED")
    bot.run(token)
