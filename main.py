import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# ─────────────────────────
# Flask Web Server (Render requires this)
# ─────────────────────────

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Start Flask server
keep_alive()


# ─────────────────────────
# Discord Bot Setup
# ─────────────────────────

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    async def setup_hook(self):
        # Load all cogs safely
        if os.path.exists("./cogs"):
            for file in os.listdir("./cogs"):
                if file.endswith(".py"):
                    try:
                        await self.load_extension(f"cogs.{file[:-3]}")
                        print(f"✅ Loaded cog: {file}")
                    except Exception as e:
                        print(f"❌ Failed to load {file}: {e}")

bot = MyBot(
    command_prefix=".",
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    print(f"🚀 Logged in as {bot.user}")


# ─────────────────────────
# Start Bot
# ─────────────────────────

token = os.getenv("TOKEN")

if not token:
    print("❌ TOKEN NOT FOUND in environment variables.")
else:
    print("✅ TOKEN LOADED")
    bot.run(token)
