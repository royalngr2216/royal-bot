from discord.ext import commands
import random
import asyncio
import discord

class Flip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='flip')
    async def flip(self, ctx):
        suspense_msg = await ctx.send("Flipping the coin... 🪙")

        suspense_texts = ["Flipping. 🪙", "Flipping.. 🪙", "Flipping... 🪙"]

        for text in suspense_texts:
            await suspense_msg.edit(content=text)
            await asyncio.sleep(0.05)

        heads_gif = "https://cdn.discordapp.com/attachments/1356735875517775995/1360904053567262883/VN20250413_143452.gif"
        tails_gif = "https://cdn.discordapp.com/attachments/1356735875517775995/1360903389403283496/VN20250413_142456_2.gif"

        result_gif = random.choice([heads_gif, tails_gif])

        embed = discord.Embed(title="🪙 Coin Flip Result", color=discord.Color.gold())
        embed.set_image(url=result_gif)

        await suspense_msg.edit(content=None, embed=embed)

async def setup(bot):
    await bot.add_cog(Flip(bot))
