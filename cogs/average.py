import discord
from discord.ext import commands
import asyncio

class AverageGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    @commands.command()
    async def average(self, ctx):
        """Start the Average Game"""

        if ctx.guild.id in self.active_games:
            return await ctx.send("⚠️ A game is already running in this server.")

        embed = discord.Embed(
            title="🎯 Average Game Started!",
            description=(
                "React with 🎮 to participate!\n\n"
                "📌 Rules:\n"
                "• Everyone chooses a secret number.\n"
                "• Bot calculates the average.\n"
                "• Average is multiplied by **0.8**.\n"
                "• Closest player wins.\n"
                "• Equal distance = Draw."
            ),
            color=discord.Color.blurple()
        )

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎮")

        await asyncio.sleep(20)

        msg = await ctx.channel.fetch_message(msg.id)

        players = []

        for reaction in msg.reactions:
            if str(reaction.emoji) == "🎮":
                async for user in reaction.users():
                    if not user.bot:
                        players.append(user)

        players = list(dict.fromkeys(players))

        if len(players) < 2:
            return await ctx.send("❌ Need at least 2 players.")

        game = {
            "players": players,
            "numbers": {},
            "current": 0,
            "channel": ctx.channel
        }

        self.active_games[ctx.guild.id] = game

        player_mentions = ", ".join(p.mention for p in players)

        await ctx.send(
            f"🎮 Players Joined:\n{player_mentions}\n\n"
            f"🔢 {players[0].mention}, choose your number using:\n"
            f"```/average number```"
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild = message.guild

        if not guild:
            return

        if guild.id not in self.active_games:
            return

        game = self.active_games[guild.id]

        current_player = game["players"][game["current"]]

        if message.author != current_player:
            return

        if not message.content.startswith("/average "):
            return

        try:
            number = float(message.content.split(" ")[1])
        except:
            return await message.channel.send("❌ Invalid number.")

        game["numbers"][message.author.id] = number

        await message.channel.send(
            f"✅ {message.author.mention} has chosen their number."
        )

        game["current"] += 1

        # More players left
        if game["current"] < len(game["players"]):
            next_player = game["players"][game["current"]]

            await message.channel.send(
                f"🔢 {next_player.mention}, it's your turn.\n"
                f"Use:\n```/average number```"
            )

        else:
            await self.finish_game(guild.id)

    async def finish_game(self, guild_id):
        game = self.active_games[guild_id]

        numbers = game["numbers"]
        players = game["players"]
        channel = game["channel"]

        values = list(numbers.values())

        avg = sum(values) / len(values)
        target = avg * 0.8

        distances = {}

        for player in players:
            num = numbers[player.id]
            distances[player.id] = abs(num - target)

        min_distance = min(distances.values())

        winners = [
            player for player in players
            if distances[player.id] == min_distance
        ]

        embed = discord.Embed(
            title="📊 Average Game Results",
            color=discord.Color.green()
        )

        result_text = ""

        for player in players:
            result_text += (
                f"👤 {player.mention} → **{numbers[player.id]}**\n"
            )

        embed.add_field(
            name="🎲 Chosen Numbers",
            value=result_text,
            inline=False
        )

        embed.add_field(
            name="📈 Calculations",
            value=(
                f"Average = **{avg:.2f}**\n"
                f"Average × 0.8 = **{target:.2f}**"
            ),
            inline=False
        )

        # Draw
        if len(winners) > 1:
            mentions = ", ".join(w.mention for w in winners)

            embed.add_field(
                name="🤝 Result",
                value=(
                    f"It's a **DRAW** between:\n{mentions}"
                ),
                inline=False
            )

        else:
            winner = winners[0]

            embed.add_field(
                name="🏆 Winner",
                value=f"{winner.mention} wins!",
                inline=False
            )

        await channel.send(embed=embed)

        del self.active_games[guild_id]


async def setup(bot):
    await bot.add_cog(AverageGame(bot))
