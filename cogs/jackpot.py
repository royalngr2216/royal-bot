from discord.ext import commands
import random
import asyncio
import discord

from utils.game_state import jackpot_games

class Jackpot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='jackpot')
    async def jackpot(self, ctx):
        if ctx.channel.id in jackpot_games:
            await ctx.send("A jackpot game is already ongoing in this channel.")
            return

        message = await ctx.send("React with 🎰 within **8 seconds** to join the jackpot!")
        await message.add_reaction("🎰")

        await asyncio.sleep(8)
        message = await ctx.channel.fetch_message(message.id)

        reaction = None
        for r in message.reactions:
            if str(r.emoji) == "🎰":
                reaction = r
                break

        players = []
        if reaction:
            async for user in reaction.users():
                if not user.bot:
                    players.append(user)

        if len(players) < 3:
            await ctx.send("Not enough players joined. Game canceled.")
            return

        jackpot_games[ctx.channel.id] = {"players": players}

        await ctx.send(
            f"🎲 Jackpot starts! {', '.join(p.mention for p in players)}"
        )

        while len(players) > 1:
            await asyncio.sleep(1)
            eliminated = random.choice(players)
            players.remove(eliminated)
            await ctx.send(f"❌ {eliminated.mention} eliminated!")

        winner = players[0]
        await ctx.send(f"🏆 {winner.mention} wins the Jackpot!")

        del jackpot_games[ctx.channel.id]

async def setup(bot):
    await bot.add_cog(Jackpot(bot))
