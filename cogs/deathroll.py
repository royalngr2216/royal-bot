from discord.ext import commands
import discord
import random

from utils.game_state import deathroll_games
from utils.stats import (
    record_win,
    record_loss,
    get_profile
)

from cogs.system import update_roles


# ─────────────────────────
# ROLL BUTTON VIEW
# ─────────────────────────

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
                "It's not your turn.",
                ephemeral=True
            )
            return

        roll = random.randint(
            1,
            game["max_number"]
        )

        current_player = interaction.user

        # ─────────────────────────
        # ROLL = 1
        # ─────────────────────────

        if roll == 1:

            if current_player == game["player1"]:

                game["score2"] += 1

                loser = game["player1"]
                winner = game["player2"]

            else:

                game["score1"] += 1

                loser = game["player2"]
                winner = game["player1"]

            game["max_number"] = 1000
            game["turn"] = winner

            embed = discord.Embed(
                title="💀 ROUND OVER",
                color=discord.Color.red()
            )

            embed.description = (
                f"🎲 {current_player.mention} rolled\n"
                f"# **1**\n\n"
                f"☠️ {loser.mention} loses the round!"
            )

            embed.add_field(
                name="📊 Score",
                value=(
                    f"# {game['score1']} - {game['score2']}"
                ),
                inline=False
            )

            await interaction.response.edit_message(
                embed=embed,
                view=None
            )

            # MATCH OVER
            if (
                game["score1"] == game["wins_required"]
                or
                game["score2"] == game["wins_required"]
            ):

                await self.cog.end_match(
                    interaction.channel,
                    self.channel_id
                )

                return

            # NEXT ROUND
            await self.cog.send_game_embed(
                interaction.channel,
                self.channel_id
            )

            return

        # ─────────────────────────
        # NORMAL ROLL
        # ─────────────────────────

        game["max_number"] = roll

        game["turn"] = (
            game["player1"]
            if current_player == game["player2"]
            else game["player2"]
        )

        embed = discord.Embed(
            title="💀 DEATHROLL ARENA",
            color=discord.Color.dark_red()
        )

        embed.description = (
            f"{game['player1'].mention} ⚔️ "
            f"{game['player2'].mention}"
        )

        embed.add_field(
            name="🎲 Roll",
            value=(
                f"{current_player.mention}\n"
                f"# **{roll}**"
            ),
            inline=False
        )

        embed.add_field(
            name="📉 New Max Number",
            value=f"# **{roll}**",
            inline=True
        )

        embed.add_field(
            name="🎯 Current Turn",
            value=game["turn"].mention,
            inline=True
        )

        embed.add_field(
            name="📊 Score",
            value=(
                f"# {game['score1']} - "
                f"{game['score2']}"
            ),
            inline=False
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
        )


# ─────────────────────────
# MAIN COG
# ─────────────────────────

class Deathroll(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # ─────────────────────────
    # START COMMAND
    # ─────────────────────────

    @commands.command(name="deathroll")
    async def deathroll(
        self,
        ctx,
        opponent: discord.Member,
        bo: int = 1
    ):

        if opponent == ctx.author:

            await ctx.send(
                "❌ You cannot play yourself."
            )
            return

        if bo not in [1, 3, 5, 7, 9]:

            await ctx.send(
                "❌ BO must be 1, 3, 5, 7, or 9."
            )
            return

        if ctx.channel.id in deathroll_games:

            await ctx.send(
                "❌ A deathroll game is already active here."
            )
            return

        wins_required = (bo // 2) + 1

        deathroll_games[ctx.channel.id] = {

            "player1": ctx.author,
            "player2": opponent,

            "score1": 0,
            "score2": 0,

            "wins_required": wins_required,

            "max_number": 1000,

            "turn": ctx.author
        }

        await self.send_game_embed(
            ctx.channel,
            ctx.channel.id
        )

    # ─────────────────────────
    # GAME EMBED
    # ─────────────────────────

    async def send_game_embed(
        self,
        channel,
        channel_id
    ):

        game = deathroll_games[channel_id]

        embed = discord.Embed(
            title="💀 DEATHROLL ARENA",
            color=discord.Color.dark_red()
        )

        embed.description = (
            f"{game['player1'].mention} ⚔️ "
            f"{game['player2'].mention}\n\n"
            f"🎯 First to "
            f"**{game['wins_required']}** wins."
        )

        embed.add_field(
            name="🎲 Max Number",
            value=f"# **{game['max_number']}**",
            inline=True
        )

        embed.add_field(
            name="📊 Score",
            value=(
                f"# {game['score1']} - "
                f"{game['score2']}"
            ),
            inline=True
        )

        embed.add_field(
            name="🕒 Current Turn",
            value=game["turn"].mention,
            inline=False
        )

        embed.set_footer(
            text="Press the button below to roll."
        )

        view = RollView(
            self,
            channel_id
        )

        await channel.send(
            embed=embed,
            view=view
        )

    # ─────────────────────────
    # MATCH END
    # ─────────────────────────

    async def end_match(
        self,
        channel,
        channel_id
    ):

        game = deathroll_games[channel_id]

        if game["score1"] > game["score2"]:

            winner = game["player1"]
            loser = game["player2"]

        else:

            winner = game["player2"]
            loser = game["player1"]

        # SAVE STATS

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

        # RESULT EMBED

        embed = discord.Embed(
            title="🏆 MATCH OVER",
            color=discord.Color.gold()
        )

        embed.description = (
            f"👑 Winner: {winner.mention}\n"
            f"💀 Loser: {loser.mention}"
        )

        embed.add_field(
            name="📊 Final Score",
            value=(
                f"# {game['score1']} - "
                f"{game['score2']}"
            ),
            inline=False
        )

        embed.set_footer(
            text="Deathroll Arena"
        )

        await channel.send(embed=embed)

        del deathroll_games[channel_id]


async def setup(bot):

    await bot.add_cog(
        Deathroll(bot)
    )
