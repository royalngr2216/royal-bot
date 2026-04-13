import discord
from discord.ext import commands

class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.maintenance = False
        self.owner_id = 1287545546231255092  # 🔴 PUT YOUR DISCORD ID HERE

    def is_owner(self, user_id):
        return user_id == self.owner_id

    @commands.command()
    async def offline(self, ctx):
        if not self.is_owner(ctx.author.id):
            return

        self.maintenance = True
        await ctx.send("🛠️ Bot is now under maintenance.")

    @commands.command()
    async def online(self, ctx):
        if not self.is_owner(ctx.author.id):
            return

        self.maintenance = False
        await ctx.send("✅ Bot is back online!")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        if self.maintenance and ctx.command.name not in ["online"]:
            await ctx.send("🛠️ Bot is currently under maintenance. Please try later.")
            raise commands.CheckFailure()

async def setup(bot):
    await bot.add_cog(Maintenance(bot))