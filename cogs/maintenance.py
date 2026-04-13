from discord.ext import commands

class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = 1287545546231255092  # 🔴 PUT YOUR DISCORD ID HERE

    def is_owner(self, user_id):
        return user_id == self.owner_id

    @commands.command()
    async def offline(self, ctx):
        if not self.is_owner(ctx.author.id):
            return

        self.bot.maintenance = True
        await ctx.send("🛠️ Bot is now under maintenance.")

    @commands.command()
    async def online(self, ctx):
        if not self.is_owner(ctx.author.id):
            return

        self.bot.maintenance = False
        await ctx.send("✅ Bot is back online!")

async def setup(bot):
    await bot.add_cog(Maintenance(bot))