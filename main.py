import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# ─────────────────────────
# Flask Web Server (Render keep-alive)
# ─────────────────────────

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Flask running on port {port}")
    app.run(host="0.0.0.0", port=port)

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
        print("⚙️ Loading cogs...")
        if os.path.exists("./cogs"):
            for file in os.listdir("./cogs"):
                if file.endswith(".py"):
                    try:
                        await self.load_extension(f"cogs.{file[:-3]}")
                        print(f"✅ Loaded cog: {file}")
                    except Exception as e:
                        print(f"❌ Failed to load {file}: {e}")
        else:
            print("⚠️ No cogs folder found")


bot = MyBot(
    command_prefix=".",
    intents=intents,
    help_command=None
)


# ─────────────────────────
# Global Check
# ─────────────────────────

@bot.check
async def global_check(ctx):
    if ctx.bot.maintenance and ctx.command.name not in ["online", "offline"]:
        await ctx.send("🛠️ Bot is currently under maintenance. Please try later.")
        return False
    return True


# ─────────────────────────
# Events
# ─────────────────────────

@bot.event
async def on_ready():
    print(f"🚀 Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    role_id = 1478375120895475866
    role = member.guild.get_role(role_id)

    if role:
        await member.add_roles(role)
        print(f"✅ Gave role to {member.name}")
    else:
        print("⚠️ Role not found")


# ─────────────────────────
# MAIN START
# ─────────────────────────

if __name__ == "__main__":
    print("🔁 Starting bot...")

    keep_alive()

    token = os.getenv("TOKEN")

    print(f"🔑 TOKEN LOADED: {token is not None}")

    if not token:
        print("❌ TOKEN NOT FOUND. Set it in Render environment variables.")
    else:
        try:
            bot.run(token)
        except Exception as e:
            print(f"❌ Error while starting bot: {e}")
