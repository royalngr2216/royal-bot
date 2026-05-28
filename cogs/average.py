import discord
from discord.ext import commands
from discord import app_commands
import asyncio


class AverageGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}

    # ─────────────────────────
    # START GAME COMMAND
    # ─────────────────────────

    @commands.command()
    async def average(self, ctx):

        if ctx.guild.id in self.active_games:
            return await ctx.send(
                "⚠️ A game is already running in this server."
            )

        embed = discord.Embed(
            title="🎯 Average Game",
            description=(
                "React with 🎮 to join!\n\n"
                "📌 Rules:\n"
                "• Everyone secretly chooses a number\n"
                "• Bot calculates average\n"
                "• Average × 0.8 becomes target\n"
                "• Closest player wins\n"
                "• Same distance = draw"
            ),
            color=discord.Color.blurple()
        )

        embed.set_footer(text="Game starts in 20 seconds")

        join_msg = await ctx.send(embed=embed)

        await join_msg.add_reaction("🎮")

        await asyncio.sleep(20)

        join_msg = await ctx.channel.fetch_message(join_msg.id)

        players = []

        for reaction in join_msg.reactions:
            if str(reaction.emoji) == "🎮":

                async for user in reaction.users():
                    if not user.bot:
                        players.append(user)

        players = list(dict.fromkeys(players))

        if len(players) < 2:
            return await ctx.send(
                "❌ Need at least 2 players to start."
            )

        game = {
            "players": players,
            "numbers": {},
            "current": 0,
            "channel": ctx.channel
        }

        self.active_games[ctx.guild.id] = game

        mentions = ", ".join([p.mention for p in players])

        start_embed = discord.Embed(
            title="🎮 Game Started!",
            description=f"Players:\n{mentions}",
            color=discord.Color.green()
        )

        start_embed.add_field(
            name="🔢 First Turn",
            value=(
                f"{players[0].mention}, choose your number using:\n"
                f"`/pick number:<your number>`"
            ),
            inline=False
        )

        await ctx.send(embed=start_embed)

    # ─────────────────────────
    # SLASH COMMAND
    # ─────────────────────────

    @app_commands.command(
        name="pick",
        description="Pick your number for Average Game"
    )
    @app_commands.describe(
        number="Your secret number"
    )
    async def pick(
        self,
        interaction: discord.Interaction,
        number: float
    ):

        guild = interaction.guild

        if not guild:
            return

        if guild.id not in self.active_games:
            return await interaction.response.send_message(
                "❌ No active game running.",
                ephemeral=True
            )

        game = self.active_games[guild.id]

        current_player = game["players"][game["current"]]

        # Wrong turn
        if interaction.user != current_player:
            return await interaction.response.send_message(
                "❌ It's not your turn.",
                ephemeral=True
            )

        # Already picked
        if interaction.user.id in game["numbers"]:
            return await interaction.response.send_message(
                "❌ You already chose a number.",
                ephemeral=True
            )

        game["numbers"][interaction.user.id] = number

        await interaction.response.send_message(
            f"✅ You secretly chose: **{number}**",
            ephemeral=True
        )

        await game["channel"].send(
            f"✅ {interaction.user.mention} has chosen their number."
        )

        game["current"] += 1

        # Next player
        if game["current"] < len(game["players"]):

            next_player = game["players"][game["current"]]

            embed = discord.Embed(
                title="🔢 Next Turn",
                description=(
                    f"{next_player.mention}, choose your number using:\n"
                    f"`/pick number:<your number>`"
                ),
                color=discord.Color.orange()
            )

            await game["channel"].send(embed=embed)

        else:
            await self.finish_game(guild.id)

    # ─────────────────────────
    # FINISH GAME
    # ─────────────────────────

    async def finish_game(self, guild_id):

        game = self.active_games[guild_id]

        players = game["players"]
        numbers = game["numbers"]
        channel = game["channel"]

        values = list(numbers.values())

        average = sum(values) / len(values)

        target = average * 0.8

        distances = {}

        for player in players:

            player_number = numbers[player.id]

            distances[player.id] = abs(
                player_number - target
            )

        min_distance = min(distances.values())

        winners = []

        for player in players:

            if distances[player.id] == min_distance:
                winners.append(player)

        result_embed = discord.Embed(
            title="📊 Average Game Results",
            color=discord.Color.purple()
        )

        number_text = ""

        for player in players:

            number_text += (
                f"{player.mention} → **{numbers[player.id]}**\n"
            )

        result_embed.add_field(
            name="🎲 Chosen Numbers",
            value=number_text,
            inline=False
        )

        result_embed.add_field(
            name="📈 Calculations",
            value=(
                f"Average = **{average:.2f}**\n"
                f"Average × 0.8 = **{target:.2f}**"
            ),
            inline=False
        )

        # DRAW
        if len(winners) > 1:

            winner_mentions = ", ".join(
                [w.mention for w in winners]
            )

            result_embed.add_field(
                name="🤝 Draw!",
                value=(
                    f"Closest distance matched between:\n"
                    f"{winner_mentions}"
                ),
                inline=False
            )

        # SINGLE WINNER
        else:

            winner = winners[0]

            result_embed.add_field(
                name="🏆 Winner",
                value=f"{winner.mention} wins!",
                inline=False
            )

        await channel.send(embed=result_embed)

        del self.active_games[guild_id]


# ─────────────────────────
# LOAD COG
# ─────────────────────────

async def setup(bot):
    await bot.add_cog(AverageGame(bot))
