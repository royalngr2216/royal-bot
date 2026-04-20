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


# ─────────────────────────
# Discord Bot Setup
# ─────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.maintenance = False
        self.owner_id = 1287545546231255092

    async def setup_hook(self):
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

@bot.check
async def global_check(ctx):
    if ctx.bot.maintenance and ctx.command.name not in ["online", "offline"]:
        await ctx.send("🛠️ Bot is currently under maintenance. Please try later.")
        return False
    return True


@bot.event
async def on_ready():
    print(f"🚀 Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    role_id = 1478375120895475866
    role = member.guild.get_role(role_id)

    if role:
        await member.add_roles(role)


# ─────────────────────────
# SAFE START (THIS FIXES YOUR ISSUE)
# ─────────────────────────

if __name__ == "__main__":
    keep_alive()

    token = os.getenv("TOKEN")

    if not token:
        print("❌ TOKEN NOT FOUND in environment variables.")
    else:
        print("✅ TOKEN LOADED")
        bot.run(token, reconnect=True)
