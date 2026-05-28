import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# ─────────────────────────
# Flask Keep Alive
# ─────────────────────────

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ─────────────────────────
# Discord Setup
# ─────────────────────────

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix=".",
            intents=intents,
            help_command=None
        )

        self.maintenance = False
        self.owner_id = 1287545546231255092

    async def setup_hook(self):

        print("⚙️ Loading cogs...")

        if os.path.exists("./cogs"):

            for file in os.listdir("./cogs"):

                if file.endswith(".py"):

                    try:

                        await self.load_extension(
                            f"cogs.{file[:-3]}"
                        )

                        print(f"✅ Loaded {file}")

                    except Exception as e:

                        print(f"❌ Failed {file}: {e}")

bot = MyBot()

# ─────────────────────────
# Global Check
# ─────────────────────────

@bot.check
async def global_check(ctx):

    if (
        bot.maintenance
        and ctx.command.name not in ["online", "offline"]
    ):

        await ctx.send(
            "🛠️ Bot under maintenance."
        )

        return False

    return True

# ─────────────────────────
# Events
# ─────────────────────────

@bot.event
async def on_ready():

    try:

        synced = await bot.tree.sync()

        print(f"🌍 Synced {len(synced)} slash commands")

    except Exception as e:

        print(e)

    print(f"🚀 Logged in as {bot.user}")

@bot.event
async def on_member_join(member):

    role_id = 1478375120895475866

    role = member.guild.get_role(role_id)

    if role:

        await member.add_roles(role)

# ─────────────────────────
# Start Bot
# ─────────────────────────

if __name__ == "__main__":

    print("🔁 Starting bot...")

    keep_alive()

    token = os.getenv("TOKEN")

    if not token:

        print("❌ TOKEN NOT FOUND")

    else:

        bot.run(token)
