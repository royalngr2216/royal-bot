from discord.ext import commands
import random
import discord
from utils.game_state import deathroll_games
from utils.stats import record_win, record_loss, get_profile
from cogs.system import update_roles


class RollView(discord.ui.View):

    def __init__(self, cog, channel_id):
        super().__init__(timeout=None)
        self.cog = cog
        self.channel_id = channel_id

    @discord.ui.button(
        label="🎲 Roll",
        style=discord.ButtonStyle.danger
    )
    async def roll_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if self.channel_id not in deathroll_games:
            await interaction.response.send_message(
                "No active deathroll game.",
                ephemeral=True
            )
            return

        game = deathroll_games[self.channel_id]

        if interaction.user != game["turn"]:
            await interaction.response.send_message(
                "Not your turn.",
                ephemeral=True
            )
            return

        roll_result = random.randint(
            1,
            game["max_number"]
        )

        current_player = interaction.user

        next_player = (
            game["player1"]
            if current_player == game["player2"]
            else game["player2"]
        )

        # ─────────────────────────
        # PLAYER ROLLED 1
        # ─────────────────────────

        if roll_result == 1:

            if current_player == game["player1"]:
                game["score2"] += 1
                winner = game["player2"]
            else:
                game["score1"] += 1
                winner = game["player1"]

            embed = discord.Embed(
                description=(
                    f"💀 {current_player.mention} rolled\n"
                    f"# **1**\n\n"
                    f"🏆 {winner.mention} wins the round!"
                ),
                color=discord.Color.dark_red()
            )

            await interaction.response.send_message(
                embed=embed
            )

            game["max_number"] = 1000
            game["turn"] = winner

            if (
                game["score1"] == game["wins_required"]
                or
                game["score2"] == game["wins_required"]
            ):
                await self.cog.end_match(
                    self.channel_id
                )
                return

            new_view = RollView(
                self.cog,
                self.channel_id
            )

            start_embed = discord.Embed(
                description=(
                    f"🎯 {winner.mention}'s turn\n"
                    f"# Roll between 1 - 1000"
                ),
                color=discord.Color.red()
            )

            await interaction.channel.send(
                embed=start_embed,
                view=new_view
            )

            return

        # ─────────────────────────
        # NORMAL ROLL
        # ─────────────────────────

        game["max_number"] = roll_result
        game["turn"] = next_player

        embed = discord.Embed(
            description=(
                f"🎲 {current_player.mention} rolled\n"
                f"# **{roll_result}**\n\n"
                f"🎯 {next_player.mention}'s turn"
            ),
            color=discord.Color.red()
        )

        new_view = RollView(
            self.cog,
            self.channel_id
        )

        await interaction.response.send_message(
            embed=embed,
            view=new_view
        )


class Deathroll(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="deathroll")
    async def deathroll(
        self,
        ctx,
        opponent: discord.Member,
        bo: int = 1
    ):

        if opponent == ctx.author:
            await ctx.send(
                "You cannot play yourself."
            )
            return

        if bo not in [1, 3, 5, 7, 9]:
            await ctx.send(
                "Use: `.deathroll @user 1/3/5/7/9`"
            )
            return

        if ctx.channel.id in deathroll_games:
            await ctx.send(
                "A deathroll game is already active."
            )
            return

        wins_required = (bo // 2) + 1

        deathroll_games[ctx.channel.id] = {
            "player1": ctx.author,
            "player2": opponent,
            "bo": bo,
            "wins_required": wins_required,
            "score1": 0,
            "score2": 0,
            "max_number": 1000,
            "turn": ctx.author
        }

        embed = discord.Embed(
            description=(
                f"{ctx.author.mention} ⚔️ "
                f"{opponent.mention}\n\n"
                f"🏆 First to {wins_required} wins\n\n"
                f"🎯 {ctx.author.mention}'s turn\n"
                f"# Roll between 1 - 1000"
            ),
            color=discord.Color.red()
        )

        view = RollView(
            self,
            ctx.channel.id
        )

        await ctx.send(
            embed=embed,
            view=view
        )

    async def end_match(self, channel_id):

        game = deathroll_games[channel_id]

        if game["score1"] > game["score2"]:
            winner = game["player1"]
            loser = game["player2"]
        else:
            winner = game["player2"]
            loser = game["player1"]

        record_win(winner.id, 0)
        record_loss(loser.id, 0)

        winner_stats = get_profile(
            winner.id
        )

        loser_stats = get_profile(
            loser.id
        )

        await update_roles(
            winner,
            winner_stats["matches"]
        )

        await update_roles(
            loser,
            loser_stats["matches"]
        )

        embed = discord.Embed(
            description=(
                f"🏆 {winner.mention} wins the match!\n\n"
                f"📊 Final Score\n"
                f"# {game['score1']} - {game['score2']}"
            ),
            color=discord.Color.gold()
        )

        channel = self.bot.get_channel(
            channel_id
        )

        await channel.send(embed=embed)

        del deathroll_games[channel_id]


async def setup(bot):
    await bot.add_cog(
        Deathroll(bot)
        )
