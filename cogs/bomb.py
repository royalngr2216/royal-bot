import discord
from discord.ext import commands
import asyncio
import random
from collections import deque

class Bomb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

        self.death_messages = [
            "💀 {user} held it too long... BOOM!",
            "🔥 {user} panicked and exploded!",
            "💥 {user} failed the timing!",
            "☠️ {user} froze... and died.",
            "🎇 {user} became fireworks!",
        ]

    async def start_timer(self, ctx, channel_id):
        await asyncio.sleep(5)

        game = self.games.get(channel_id)
        if not game:
            return

        holder = game["holder"]

        msg = random.choice(self.death_messages).format(user=holder.mention)
        await ctx.send(msg)

        game["players"].remove(holder)

        if len(game["players"]) == 1:
            winner = game["players"][0]
            await ctx.send(f"🏆 **{winner.mention} wins the game!**")
            self.games.pop(channel_id)
            return

        # New round
        new_holder = random.choice(game["players"])
        game["holder"] = new_holder
        game["turn"] = 0
        game["explode_at"] = random.randint(len(game["players"])*3, len(game["players"])*5)

        await ctx.send(f"💣 New round! {new_holder.mention} has the bomb!")

        # Restart timer
        game["timer"] = asyncio.create_task(self.start_timer(ctx, channel_id))

    @commands.command()
    async def bomb(self, ctx):
        if ctx.channel.id in self.games:
            return await ctx.send("❌ A bomb game is already running!")

        msg = await ctx.send("💣 **Bomb Game Starting!**\nReact with 🎮 to join (10s)")
        await msg.add_reaction("🎮")

        await asyncio.sleep(10)

        msg = await ctx.fetch_message(msg.id)

        users = []
        for reaction in msg.reactions:
            if str(reaction.emoji) == "🎮":
                users = [u async for u in reaction.users() if not u.bot]

        if len(users) < 3:
            return await ctx.send("❌ Need at least 3 players!")

        holder = random.choice(users)

        game = {
            "players": users,
            "holder": holder,
            "last": deque(maxlen=3),
            "turn": 0,
            "explode_at": random.randint(len(users)*3, len(users)*5),
            "timer": None
        }

        self.games[ctx.channel.id] = game

        await ctx.send(
            f"💣 **The bomb is LIVE!**\n"
            f"🎯 Holder: {holder.mention}\n"
            f"⏱ You have **5 seconds** to pass!"
        )

        # Start timer
        game["timer"] = asyncio.create_task(self.start_timer(ctx, ctx.channel.id))

    @commands.command(name="pass")
    async def pass_bomb(self, ctx, member: discord.Member):
        game = self.games.get(ctx.channel.id)

        if not game:
            return await ctx.send("❌ No active bomb game!")

        if ctx.author != game["holder"]:
            return await ctx.send("❌ You don't have the bomb!")

        if member not in game["players"]:
            return await ctx.send("❌ That user is not in the game!")

        if member == ctx.author:
            return await ctx.send("❌ You can't pass to yourself!")

        if member in game["last"]:
            return await ctx.send("❌ That player recently had the bomb!")

        # Cancel old timer
        if game["timer"]:
            game["timer"].cancel()

        game["last"].append(game["holder"])
        game["holder"] = member
        game["turn"] += 1

        # 🔥 tension message
        if random.random() < 0.4:
            await ctx.send("🔥 **The bomb is heating up...**")

        # Explosion by turn
        if game["turn"] >= game["explode_at"]:
            msg = random.choice(self.death_messages).format(user=member.mention)
            await ctx.send(msg)

            game["players"].remove(member)

            if len(game["players"]) == 1:
                winner = game["players"][0]
                await ctx.send(f"🏆 **{winner.mention} wins!**")
                self.games.pop(ctx.channel.id)
                return

            new_holder = random.choice(game["players"])
            game["holder"] = new_holder
            game["turn"] = 0

            await ctx.send(f"💣 New round! {new_holder.mention} has the bomb!")

            game["timer"] = asyncio.create_task(self.start_timer(ctx, ctx.channel.id))
            return

        await ctx.send(
            f"➡️ {ctx.author.mention} ➜ {member.mention}\n"
            f"⏱ **5s to pass!**"
        )

        # Restart timer
        game["timer"] = asyncio.create_task(self.start_timer(ctx, ctx.channel.id))

async def setup(bot):
    await bot.add_cog(Bomb(bot))