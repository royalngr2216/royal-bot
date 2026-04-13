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
            "🔥 {user} got nervous... exploded!",
            "💥 {user} fumbled the bomb!",
            "☠️ {user} tried to act cool... didn't work.",
            "🎇 {user} became fireworks!",
        ]

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
            "active": True
        }

        self.games[ctx.channel.id] = game

        await ctx.send(
            f"💣 **The bomb is LIVE!**\n"
            f"🎯 Holder: {holder.mention}\n"
            f"⚠️ Pass quickly using `.pass @user`"
        )

    @commands.command(name="pass")
    async def pass_bomb(self, ctx, member: discord.Member):
        game = self.games.get(ctx.channel.id)

        if not game or not game["active"]:
            return await ctx.send("❌ No active bomb game!")

        if ctx.author != game["holder"]:
            return await ctx.send("❌ You don't have the bomb!")

        if member not in game["players"]:
            return await ctx.send("❌ That user is not in the game!")

        if member == ctx.author:
            return await ctx.send("❌ You can't pass to yourself!")

        if member in game["last"]:
            return await ctx.send("❌ That player just had the bomb! Choose someone else.")

        # Update history
        game["last"].append(game["holder"])
        game["holder"] = member
        game["turn"] += 1

        # 🔥 Random tension warning
        if random.random() < 0.3:
            await ctx.send("🔥 **The bomb is getting HOT...**")

        # 💥 Explosion check
        if game["turn"] >= game["explode_at"]:
            msg = random.choice(self.death_messages).format(user=member.mention)
            await ctx.send(msg)

            game["players"].remove(member)

            if len(game["players"]) == 1:
                winner = game["players"][0]
                await ctx.send(f"🏆 **{winner.mention} is the last survivor!**")
                self.games.pop(ctx.channel.id)
                return

            # New round
            new_holder = random.choice(game["players"])
            game["holder"] = new_holder
            game["turn"] = 0
            game["explode_at"] = random.randint(len(game["players"])*3, len(game["players"])*5)

            return await ctx.send(
                f"💣 **New Round!**\n"
                f"🎯 {new_holder.mention} starts with the bomb!"
            )

        # ⏱ Countdown vibe
        fake_timer = random.randint(2, 6)

        await ctx.send(
            f"➡️ {ctx.author.mention} passed the bomb to {member.mention}\n"
            f"⏱ **Tick... {fake_timer}s**"
        )

async def setup(bot):
    await bot.add_cog(Bomb(bot))