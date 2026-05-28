from discord.ext import commands
import random
import discord

from utils.game_state import crack_games
from utils.stats import (
    record_win,
    record_loss,
    get_profile
)

from cogs.system import update_roles


class Crack(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # ─────────────────────────
    # START GAME
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
                "You cannot play yourself."
            )
            return

        if bo not in [1, 3, 5, 7, 9]:

            await ctx.send(
                "Use: `.crack @user 1/3/5/7/9`"
            )
            return

        if ctx.channel.id in crack_games:

            await ctx.send(
                "A crack game is already active."
            )
            return

        wins_required = (
            bo // 2
        ) + 1

        number = random.randint(
            1,
            100
        )

        crack_games[ctx.channel.id] = {

            "player1": ctx.author,
            "player2": opponent,

            "bo": bo,

            "wins_required": wins_required,

            "score1": 0,
            "score2": 0,

            "number": number,

            "turn": ctx.author
        }

        embed = discord.Embed(
            title="🎯 CRACK ARENA",
            description=(
                f"{ctx.author.mention} ⚔️ {opponent.mention}\n\n"
                f"🏆 First to **{wins_required}** wins\n\n"
                f"🎲 Hidden Number: **1 - 100**\n\n"
                f"Use `.guess number`"
            ),
            color=discord.Color.blue()
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
                "No active crack game."
            )
            return

        game = crack_games[ctx.channel.id]

        if ctx.author != game["turn"]:

            await ctx.send(
                "It's not your turn."
            )
            return

        if not 1 <= number <= 100:

            await ctx.send(
                "Guess must be between 1 and 100."
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
                title="🏆 CORRECT GUESS",
                description=(
                    f"{ctx.author.mention} guessed the number!\n\n"
                    f"🎯 Number was **{target}**"
                ),
                color=discord.Color.green()
            )

            await ctx.send(embed=embed)

            # MATCH END

            if (
                game["score1"]
                == game["wins_required"]
                or
                game["score2"]
                == game["wins_required"]
            ):

                await self.end_match(
                    ctx.channel.id
                )

                return

            # NEW ROUND

            new_number = random.randint(
                1,
                100
            )

            game["number"] = new_number

            game["turn"] = ctx.author

            next_embed = discord.Embed(
                description=(
                    f"🎯 New round started\n\n"
                    f"Current Turn => {ctx.author.mention}"
                ),
                color=discord.Color.blurple()
            )

            await ctx.send(embed=next_embed)

            return

        # ─────────────────────────
        # WRONG GUESS
        # ─────────────────────────

        if number < target:
            hint_text = "⬆️ Go Higher"
        else:
            hint_text = "⬇️ Go Lower"

        next_turn = (
            game["player1"]
            if ctx.author == game["player2"]
            else game["player2"]
        )

        game["turn"] = next_turn

        embed = discord.Embed(
            title="❌ WRONG GUESS",
            description=(
                f"## {hint_text}\n\n"
                f"Current Turn => {next_turn.mention}"
            ),
            color=discord.Color.red()
        )

        await ctx.send(embed=embed)

    # ─────────────────────────
    # END MATCH
    # ─────────────────────────

    async def end_match(self, channel_id):

        game = crack_games[channel_id]

        if game["score1"] > game["score2"]:

            winner = game["player1"]
            loser = game["player2"]

        else:

            winner = game["player2"]
            loser = game["player1"]

        # STATS

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

        channel = self.bot.get_channel(
            channel_id
        )

        embed = discord.Embed(
            description=(
                f"🏆 {winner.mention} wins the match!\n\n"
                f"📊 Final Score\n"
                f"**{game['score1']} - {game['score2']}**"
            ),
            color=discord.Color.gold()
        )

        await channel.send(embed=embed)

        del crack_games[channel_id]


async def setup(bot):

    await bot.add_cog(
        Crack(bot)
    )
