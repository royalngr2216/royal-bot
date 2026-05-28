from discord.ext import commands
import discord
import random

from utils.game_state import crack_games

from utils.stats import (
    record_win,
    record_loss,
    get_profile
)

from cogs.system import update_roles


# ─────────────────────────
# CRACK COG
# ─────────────────────────

class Crack(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # ─────────────────────────
    # START MATCH
    # ─────────────────────────

    @commands.command(name="crack")
    async def crack(
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

        if ctx.channel.id in crack_games:

            await ctx.send(
                "❌ A crack game is already active here."
            )
            return

        wins_required = (bo // 2) + 1

        crack_games[ctx.channel.id] = {

            "player1": ctx.author,
            "player2": opponent,

            "score1": 0,
            "score2": 0,

            "wins_required": wins_required,

            "number": random.randint(1, 100),

            "turn": ctx.author
        }

        embed = discord.Embed(
            title="🎯 CRACK ARENA",
            color=discord.Color.blurple()
        )

        embed.description = (
            f"{ctx.author.mention} ⚔️ "
            f"{opponent.mention}\n\n"
            f"🏆 First to "
            f"**{wins_required}** wins."
        )

        embed.add_field(
            name="🎮 How To Play",
            value=(
                "Use:\n"
                "` .guess number `\n\n"
                "Example:\n"
                "` .guess 50 `"
            ),
            inline=False
        )

        embed.add_field(
            name="📊 Score",
            value="# 0 - 0",
            inline=True
        )

        embed.add_field(
            name="🕒 Current Turn",
            value=ctx.author.mention,
            inline=True
        )

        embed.set_footer(
            text="Hidden Number: 1 - 100"
        )

        await ctx.send(embed=embed)

    # ─────────────────────────
    # GUESS COMMAND
    # ─────────────────────────

    @commands.command(name="guess")
    async def guess(
        self,
        ctx,
        number: int
    ):

        if ctx.channel.id not in crack_games:

            await ctx.send(
                "❌ No active crack game."
            )
            return

        game = crack_games[ctx.channel.id]

        if ctx.author != game["turn"]:

            await ctx.send(
                "❌ It's not your turn."
            )
            return

        if number < 1 or number > 100:

            await ctx.send(
                "❌ Guess must be between 1 and 100."
            )
            return

        target = game["number"]

        # ─────────────────────────
        # CORRECT GUESS
        # ─────────────────────────

        if number == target:

            if ctx.author == game["player1"]:

                game["score1"] += 1

            else:

                game["score2"] += 1

            embed = discord.Embed(
                title="🎉 CORRECT GUESS",
                color=discord.Color.green()
            )

            embed.description = (
                f"{ctx.author.mention} guessed\n"
                f"# **{target}**"
            )

            embed.add_field(
                name="📊 Score",
                value=(
                    f"# {game['score1']} - "
                    f"{game['score2']}"
                ),
                inline=False
            )

            await ctx.send(embed=embed)

            # MATCH END

            if (
                game["score1"] == game["wins_required"]
                or
                game["score2"] == game["wins_required"]
            ):

                await self.end_match(
                    ctx.channel
                )

                return

            # NEW ROUND

            game["number"] = random.randint(
                1,
                100
            )

            embed = discord.Embed(
                title="🎯 NEW ROUND",
                color=discord.Color.blurple()
            )

            embed.description = (
                f"🕒 {ctx.author.mention} "
                f"starts again."
            )

            embed.add_field(
                name="📊 Score",
                value=(
                    f"# {game['score1']} - "
                    f"{game['score2']}"
                ),
                inline=False
            )

            await ctx.send(embed=embed)

            return

        # ─────────────────────────
        # WRONG GUESS
        # ─────────────────────────

        if number < target:

            hint = "📈 Go Higher"

        else:

            hint = "📉 Go Lower"

        game["turn"] = (

            game["player1"]

            if ctx.author == game["player2"]

            else game["player2"]

        )

        embed = discord.Embed(
            title="❌ WRONG GUESS",
            color=discord.Color.red()
        )

        embed.description = hint

        embed.add_field(
            name="🎲 Last Guess",
            value=f"# {number}",
            inline=True
        )

        embed.add_field(
            name="🕒 Current Turn",
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

        await ctx.send(embed=embed)

    # ─────────────────────────
    # END MATCH
    # ─────────────────────────

    async def end_match(self, channel):

        game = crack_games[channel.id]

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

        # FINAL EMBED

        embed = discord.Embed(
            title="👑 CRACK WINNER",
            color=discord.Color.gold()
        )

        embed.description = (
            f"🏆 {winner.mention}\n"
            f"defeated\n"
            f"💀 {loser.mention}"
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
            text="Crack Arena"
        )

        await channel.send(embed=embed)

        del crack_games[channel.id]


async def setup(bot):

    await bot.add_cog(
        Crack(bot)
    )
