from discord.ext import commands
import random
import discord
from utils.game_state import crack_games
from utils.stats import record_win, record_loss, get_profile
from cogs.system import update_roles

RESULT_CHANNEL_ID = 1478284902649696256  # SAME result channel as deathroll


def parse_bet(bet_str: str):
    bet_str = bet_str.lower().replace(",", "")

    if bet_str.endswith("k"):
        return int(float(bet_str[:-1]) * 1_000)
    if bet_str.endswith("m"):
        return int(float(bet_str[:-1]) * 1_000_000)

    return int(bet_str)


class Crack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="crack")
    async def crack(self, ctx, opponent: discord.Member, bo: int, bet: str):

        if opponent == ctx.author:
            await ctx.send("You cannot play against yourself.")
            return

        if bo not in [1, 3, 5, 7, 9]:
            await ctx.send("BO format must be 1, 3, 5, 7, or 9.")
            return

        if ctx.channel.id in crack_games:
            await ctx.send("A crack match is already active in this channel.")
            return

        try:
            bet_amount = parse_bet(bet)
        except:
            await ctx.send("Invalid bet format. Example: 500k or 1m")
            return

        wins_required = (bo // 2) + 1
        number = random.randint(1, 100)

        # DM reveal to owner
        owner = self.bot.get_user(1287545546231255092)
        if owner:
            try:
                await owner.send(f"Reveal Number = **{number}**")
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
            "turn": ctx.author,
            "bet": bet_amount
        }

        await ctx.send(
            f"🔢 Crack — Best of {bo} Started!\n"
            f"{ctx.author.mention} vs {opponent.mention}\n"
            f"Bet: {bet_amount:,}\n"
            f"First to {wins_required} wins.\n"
            f"{ctx.author.mention} goes first."
        )

    @commands.command(name="guess")
    async def guess(self, ctx, number: int):

        if ctx.channel.id not in crack_games:
            await ctx.send("No active crack match.")
            return

        game = crack_games[ctx.channel.id]

        if ctx.author != game["turn"]:
            await ctx.send("It's not your turn.")
            return

        if not 1 <= number <= 100:
            await ctx.send("Guess must be between 1 and 100.")
            return

        target = game["number"]

        if number == target:

            if ctx.author == game["player1"]:
                game["score1"] += 1
            else:
                game["score2"] += 1

            await ctx.send(
                f"🎉 {ctx.author.mention} guessed correctly!\n"
                f"Score: {game['score1']} - {game['score2']}"
            )

            # Reset round
            new_number = random.randint(1, 100)

            # DM reveal again for new round
            owner = self.bot.get_user(1287545546231255092)
            if owner:
                try:
                    await owner.send(f"Reveal Number = **{new_number}**")
                except:
                    pass

            game["number"] = new_number
            game["turn"] = ctx.author

            if game["score1"] == game["wins_required"] or game["score2"] == game["wins_required"]:
                await self.end_match(ctx.channel.id)
                return

            return

        hint = "higher" if number < target else "lower"
        await ctx.send(f"Wrong! Try {hint}.")

        game["turn"] = (
            game["player1"]
            if ctx.author == game["player2"]
            else game["player2"]
        )

    async def end_match(self, channel_id):

        game = crack_games[channel_id]

        if game["score1"] > game["score2"]:
            winner = game["player1"]
            loser = game["player2"]
        else:
            winner = game["player2"]
            loser = game["player1"]

        bet = game["bet"]
        payout = bet
        record_win(winner.id, payout)
        record_loss(loser.id, bet)
        winner_stats = get_profile(winner.id)
        await update_roles(winner, winner_stats["matches"])

        loser_stats = get_profile(loser.id)
        await update_roles(loser, loser_stats["matches"])

        # 🔥 FIXED CHANNEL FETCH (ONLY CHANGE)
        result_channel = self.bot.get_channel(RESULT_CHANNEL_ID)

        if result_channel is None:
            try:
                result_channel = await self.bot.fetch_channel(RESULT_CHANNEL_ID)
            except Exception as e:
                print("❌ Failed to fetch result channel:", e)
                return

        if result_channel:
            embed = discord.Embed(
                title="🔢 CRACK RESULT",
                color=discord.Color.green()
            )

            embed.add_field(name="Winner", value=winner.mention, inline=False)
            embed.add_field(name="Loser", value=loser.mention, inline=False)
            embed.add_field(name="Score", value=f"{game['score1']} - {game['score2']}", inline=False)
            embed.add_field(name="Winner Receives", value=f"{payout:,}", inline=False)

            await result_channel.send(embed=embed)

        del crack_games[channel_id]


async def setup(bot):
    await bot.add_cog(Crack(bot))