from discord.ext import commands
import random
import discord

from utils.game_state import deathroll_games

from utils.stats import (
    record_win,
    record_loss,
    get_profile
)

from cogs.system import update_roles


class Deathroll(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ─────────────────────────
    # START MATCH
    # ─────────────────────────

    @commands.command(name="deathroll")
    async def deathroll(
        self,
        ctx,
        opponent: discord.Member,
        bo: int,
        *extra
    ):

        # OLD FORMAT DETECTION
        if extra:

            return await ctx.send(
                "❌ Betting system removed.\n"
                "Use:\n"
                "`.deathroll @user 3`"
            )

        if opponent == ctx.author:

            await ctx.send(
                "You cannot play against yourself."
            )

            return

        if bo not in [1, 3, 5, 7, 9]:

            await ctx.send(
                "BO format must be 1, 3, 5, 7, or 9."
            )

            return

        if ctx.channel.id in deathroll_games:

            await ctx.send(
                "A deathroll match is already active in this channel."
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

        await ctx.send(

            f"⚔️ Deathroll — BO{bo} Started!\n\n"

            f"{ctx.author.mention} ⚔️ "
            f"{opponent.mention}\n\n"

            f"🏆 First to "
            f"{wins_required} wins.\n\n"

            f"{ctx.author.mention} rolls first.\n\n"

            f"Use `.roll`"

        )

    # ─────────────────────────
    # ROLL COMMAND
    # ─────────────────────────

    @commands.command(name="roll")
    async def roll(self, ctx):

        if ctx.channel.id not in deathroll_games:

            await ctx.send(
                "No active deathroll match."
            )

            return

        game = deathroll_games[ctx.channel.id]

        if ctx.author != game["turn"]:

            await ctx.send(
                "It's not your turn."
            )

            return

        roll_result = random.randint(
            1,
            game["max_number"]
        )

        await ctx.send(

            f"🎲 {ctx.author.mention} rolled\n"
            f"## **{roll_result}**"

        )

        # ROLLED 1
        if roll_result == 1:

            if ctx.author == game["player1"]:

                game["score2"] += 1

                loser = game["player1"]
                winner = game["player2"]

            else:

                game["score1"] += 1

                loser = game["player2"]
                winner = game["player1"]

            await ctx.send(

                f"💀 {loser.mention} rolled "
                f"**1** and loses the round!\n\n"

                f"📊 Score:\n"
                f"**{game['score1']}**"
                f" - "
                f"**{game['score2']}**"

            )

            # RESET
            game["max_number"] = 1000

            game["turn"] = winner

            # MATCH END
            if (

                game["score1"]
                ==
                game["wins_required"]

                or

                game["score2"]
                ==
                game["wins_required"]

            ):

                await self.end_match(
                    ctx.channel.id
                )

                return

            return

        # CONTINUE MATCH
        game["max_number"] = roll_result

        game["turn"] = (

            game["player1"]

            if ctx.author
            ==
            game["player2"]

            else

            game["player2"]
        )

        await ctx.send(

            f"📉 New max number:\n"
            f"## **{roll_result}**\n\n"

            f"🎯 {game['turn'].mention}'s turn."

        )

    # ─────────────────────────
    # END MATCH
    # ─────────────────────────

    async def end_match(
        self,
        channel_id
    ):

        game = deathroll_games[channel_id]

        # WINNER
        if game["score1"] > game["score2"]:

            winner = game["player1"]
            loser = game["player2"]

        else:

            winner = game["player2"]
            loser = game["player1"]

        # SAVE STATS
        record_win(
            winner.id,
            0
        )

        record_loss(
            loser.id,
            0
        )

        # UPDATE ROLES
        winner_stats = get_profile(
            winner.id
        )

        await update_roles(
            winner,
            winner_stats["matches"]
        )

        loser_stats = get_profile(
            loser.id
        )

        await update_roles(
            loser,
            loser_stats["matches"]
        )

        # RESULT EMBED
        embed = discord.Embed(
            title="⚔️ DEATHROLL RESULT",
            color=discord.Color.red()
        )

        embed.add_field(
            name="🏆 Winner",
            value=winner.mention,
            inline=False
        )

        embed.add_field(
            name="💀 Loser",
            value=loser.mention,
            inline=False
        )

        embed.add_field(
            name="📊 Final Score",
            value=(
                f"**{game['score1']}**"
                f" - "
                f"**{game['score2']}**"
            ),
            inline=False
        )

        channel = self.bot.get_channel(
            channel_id
        )

        await channel.send(
            embed=embed
        )

        # CLEANUP
        del deathroll_games[channel_id]


async def setup(bot):

    await bot.add_cog(
        Deathroll(bot)
    )
