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
        bo: int,
        *extra
    ):

        # OLD FORMAT DETECTION
        if extra:

            return await ctx.send(
                "❌ Betting system removed.\n"
                "Use:\n"
                "`.crack @user 3`"
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

        if ctx.channel.id in crack_games:

            await ctx.send(
                "A crack match is already active in this channel."
            )

            return

        wins_required = (bo // 2) + 1

        number = random.randint(1, 100)

        # OWNER REVEAL
        owner = self.bot.get_user(
            1287545546231255092
        )

        if owner:

            try:

                await owner.send(
                    f"Reveal Number = **{number}**"
                )

            except:
                pass

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

        await ctx.send(

            f"🔢 Crack — Best of {bo} Started!\n\n"

            f"{ctx.author.mention} ⚔️ "
            f"{opponent.mention}\n\n"

            f"🏆 First to "
            f"{wins_required} wins.\n\n"

            f"{ctx.author.mention} goes first."

        )

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
                "No active crack match."
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

        # CORRECT
        if number == target:

            if ctx.author == game["player1"]:

                game["score1"] += 1

            else:

                game["score2"] += 1

            await ctx.send(

                f"🎉 {ctx.author.mention} "
                f"guessed correctly!\n\n"

                f"📊 Score:\n"
                f"**{game['score1']}** - "
                f"**{game['score2']}**"

            )

            # NEW ROUND
            new_number = random.randint(
                1,
                100
            )

            owner = self.bot.get_user(
                1287545546231255092
            )

            if owner:

                try:

                    await owner.send(
                        f"Reveal Number = **{new_number}**"
                    )

                except:
                    pass

            game["number"] = new_number

            game["turn"] = ctx.author

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

        # WRONG
        hint = (

            "📈 Higher"

            if number < target

            else

            "📉 Lower"

        )

        await ctx.send(
            f"❌ Wrong guess.\n{hint}"
        )

        # SWITCH TURN
        game["turn"] = (

            game["player1"]

            if ctx.author
            ==
            game["player2"]

            else

            game["player2"]
        )

    # ─────────────────────────
    # END MATCH
    # ─────────────────────────

    async def end_match(
        self,
        channel_id
    ):

        game = crack_games[channel_id]

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
            title="🔢 CRACK RESULT",
            color=discord.Color.green()
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
        del crack_games[channel_id]


async def setup(bot):

    await bot.add_cog(
        Crack(bot)
    )
