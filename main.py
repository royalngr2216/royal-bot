import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
import asyncio

# ─────────────────────────
# Flask Web Server (for Render Web Service)
# ─────────────────────────

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    thread = Thread(target=run_web)
    thread.start()


# ─────────────────────────
# Discord Bot Setup
# ─────────────────────────

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=".",
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

async def load_cogs():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")

async def main():
    # Start Flask server first
    keep_alive()

    token = os.getenv("TOKEN")

    if not token:
        print("❌ TOKEN NOT FOUND in environment variables.")
        return
    else:
        print("✅ TOKEN LOADED")

    async with bot:
        await load_cogs()
        await bot.start(token)

# Run the bot
asyncio.run(main())
