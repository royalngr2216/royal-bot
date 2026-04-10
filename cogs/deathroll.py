from discord.ext import commands
import random
import discord
from utils.game_state import deathroll_games
from utils.stats import record_win, record_loss, get_profile
from cogs.system import update_roles

RESULT_CHANNEL_ID = 1478284902649696256  # CHANGE THIS


def parse_bet(bet_str: str):
    bet_str = bet_str.lower().replace(",", "")

    if bet_str.endswith("k"):
        return int(float(bet_str[:-1]) * 1_000)
    if bet_str.endswith("m"):
        return int(float(bet_str[:-1]) * 1_000_000)

    return int(bet_str)


class Deathroll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="deathroll")
    async def deathroll(self, ctx, opponent: discord.Member, bo: int, bet: str):
        
        if opponent == ctx.author:
            await ctx.send("You cannot play against yourself.")
            return
    
        if bo not in [1, 3, 5, 7, 9]:
            await ctx.send("BO format must be 1, 3, or 5.")
            return

        if ctx.channel.id in deathroll_games:
            await ctx.send("A deathroll match is already active in this channel.")
            return

        try:
            bet_amount = parse_bet(bet)
        except:
            await ctx.send("Invalid bet format. Example: 500k or 1m")
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
            "turn": ctx.author,
            "bet": bet_amount
        }

        await ctx.send(
            f"⚔️ Deathroll BO{bo} Started!\n"
            f"{ctx.author.mention} vs {opponent.mention}\n"
            f"Bet: {bet_amount:,}\n"
            f"First to {wins_required} wins."
        )

    @commands.command(name="roll")
    async def roll(self, ctx):

        if ctx.channel.id not in deathroll_games:
            await ctx.send("No active deathroll match.")
            return

        game = deathroll_games[ctx.channel.id]

        if ctx.author != game["turn"]:
            await ctx.send("It's not your turn.")
            return

        roll_result = random.randint(1, game["max_number"])
        await ctx.send(f"{ctx.author.mention} rolled **{roll_result}**!")

        if roll_result == 1:
            # Round lost
            if ctx.author == game["player1"]:
                game["score2"] += 1
                loser = game["player1"]
                winner = game["player2"]
            else:
                game["score1"] += 1
                loser = game["player2"]
                winner = game["player1"]

            await ctx.send(
                f"💀 {loser.mention} rolled 1 and loses the round!\n"
                f"Score: {game['score1']} - {game['score2']}"
            )

            # Reset round
            game["max_number"] = 1000
            game["turn"] = winner

            # Check match win
            if game["score1"] == game["wins_required"] or game["score2"] == game["wins_required"]:
                await self.end_match(ctx.channel.id)
                return

            return

        game["max_number"] = roll_result
        game["turn"] = (
            game["player1"]
            if ctx.author == game["player2"]
            else game["player2"]
        )

    async def end_match(self, channel_id):

        game = deathroll_games[channel_id]

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
        # 🔥 ADD ROLE UPDATE
        winner_stats = get_profile(winner.id)
        await update_roles(winner, winner_stats["matches"])
        loser_stats = get_profile(loser.id)
        await update_roles(loser, loser_stats["matches"])

        # KEEP EVERYTHING BELOW SAME
       result_channel = self.bot.get_channel(RESULT_CHANNEL_ID)

        if result_channel:
            embed = discord.Embed(
                title="⚔️ DEATHROLL RESULT",
                color=discord.Color.red()
            )

            embed.add_field(name="Winner", value=winner.mention, inline=False)
            embed.add_field(name="Loser", value=loser.mention, inline=False)
            embed.add_field(name="Score", value=f"{game['score1']} - {game['score2']}", inline=False)
            embed.add_field(name="Winner Receives", value=f"{payout:,}", inline=False)

            await result_channel.send(embed=embed)

        del deathroll_games[channel_id]


async def setup(bot):
    await bot.add_cog(Deathroll(bot))
