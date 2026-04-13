import discord
from discord.ext import commands

class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.maintenance = False
        self.owner_id = 1287545546231255092  # 🔴 YOUR ID

    def is_owner(self, user_id):
        return user_id == self.owner_id

    def cog_check(self, ctx):
        # Allow only owner to use offline/online
        if ctx.command.name in ["offline", "online"]:
            return self.is_owner(ctx.author.id)

        # Block EVERYTHING else during maintenance (including owner)
        if self.maintenance:
            raise commands.CheckFailure("Bot is under maintenance.")

        return True

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
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("🛠️ Bot is currently under maintenance. Please try later.")

async def setup(bot):
    await bot.add_cog(Maintenance(bot))