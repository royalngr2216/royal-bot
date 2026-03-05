from discord.ext import commands
import random
import discord
from data.pokemon import POKEMON_LIST
from utils.stats import record_win, record_loss
from utils.game_state import randoms_games

RESULT_CHANNEL_ID = 1478284902649696256  # 🔴 REPLACE WITH YOUR RESULT CHANNEL ID


def parse_bet(bet_str: str):
    bet_str = bet_str.lower().replace(",", "")

    if bet_str.endswith("k"):
        return int(float(bet_str[:-1]) * 1_000)
    if bet_str.endswith("m"):
        return int(float(bet_str[:-1]) * 1_000_000)

    return int(bet_str)


class Randoms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="randoms")
    async def randoms(self, ctx, opponent: discord.Member, bo: int, bet: str):

        if opponent == ctx.author:
            await ctx.send("You cannot play against yourself.")
            return

        if bo not in [1, 3, 5, 7, 9]:
            await ctx.send("BO format must be 1, 3, 5, 7, or 9.")
            return

        if ctx.channel.id in randoms_games:
            await ctx.send("A randoms match is already active in this channel.")
            return

        try:
            bet_amount = parse_bet(bet)
        except:
            await ctx.send("Invalid bet format. Example: 500k or 1m")
            return

        wins_required = (bo // 2) + 1

        randoms_games[ctx.channel.id] = {
            "player1": ctx.author,
            "player2": opponent,
            "bo": bo,
            "wins_required": wins_required,
            "score1": 0,
            "score2": 0,
            "picks": {},
            "bet": bet_amount
        }

        await ctx.send(
            f"🐉 Randoms — Best of {bo} Started!\n"
            f"{ctx.author.mention} vs {opponent.mention}\n"
            f"Bet: {bet_amount:,}\n"
            f"First to {wins_required} wins.\n\n"
            f"Both players type `.pick` to start each round."
        )

    @commands.command(name="pick")
    async def pick(self, ctx):

        if ctx.channel.id not in randoms_games:
            await ctx.send("No active randoms match.")
            return

        game = randoms_games[ctx.channel.id]

        if ctx.author not in [game["player1"], game["player2"]]:
            await ctx.send("You are not part of this match.")
            return

        if ctx.author in game["picks"]:
            await ctx.send("You already picked this round.")
            return

        pokemon = random.choice(POKEMON_LIST)
        game["picks"][ctx.author] = pokemon

        # 🔥 Clean Pokémon name for GIF URL
        clean_name = (
            pokemon.name.lower()
            .replace(" ", "")
            .replace(".", "")
            .replace("'", "")
        )

        gif_url = f"https://play.pokemonshowdown.com/sprites/xyani/{clean_name}.gif"

        # 🔥 Color based on strength
        if pokemon.total_stats < 400:
            embed_color = discord.Colour.green()
        elif pokemon.total_stats < 500:
            embed_color = discord.Colour.blue()
        else:
            embed_color = discord.Colour.red()

        embed = discord.Embed(
            title=f"{ctx.author.display_name} picked {pokemon.name}",
            color=embed_color
        )

        embed.set_image(url=gif_url)

        embed.add_field(name="HP", value=pokemon.hp, inline=True)
        embed.add_field(name="Attack", value=pokemon.attack, inline=True)
        embed.add_field(name="Defense", value=pokemon.defense, inline=True)
        embed.add_field(name="Sp. Attack", value=pokemon.sp_attack, inline=True)
        embed.add_field(name="Sp. Defense", value=pokemon.sp_defense, inline=True)
        embed.add_field(name="Speed", value=pokemon.speed, inline=True)
        embed.add_field(name="Total Base Power", value=pokemon.total_stats, inline=False)

        await ctx.send(embed=embed)

        # Resolve round if both picked
        if len(game["picks"]) == 2:
            await self.resolve_round(ctx.channel.id)

    async def resolve_round(self, channel_id):

        game = randoms_games[channel_id]
        p1 = game["player1"]
        p2 = game["player2"]

        poke1 = game["picks"][p1]
        poke2 = game["picks"][p2]

        channel = self.bot.get_channel(channel_id)

        if poke1.total_stats > poke2.total_stats:
            game["score1"] += 1
            winner = p1
        elif poke2.total_stats > poke1.total_stats:
            game["score2"] += 1
            winner = p2
        else:
            winner = None

        if winner:
            await channel.send(
                f"🏆 {winner.mention} wins the round!\n"
                f"Score: {game['score1']} - {game['score2']}"
            )
        else:
            await channel.send("Round tied! No points awarded.")

        game["picks"] = {}

        if game["score1"] == game["wins_required"] or game["score2"] == game["wins_required"]:
            await self.end_match(channel_id)

    async def end_match(self, channel_id):

        game = randoms_games[channel_id]

        if game["score1"] > game["score2"]:
            winner = game["player1"]
            loser = game["player2"]
        else:
            winner = game["player2"]
            loser = game["player1"]

        bet = game["bet"]
        payout = bet - fee
        
        record_win(winner.id, payout)
        record_loss(loser.id, bet)
        result_channel = self.bot.get_channel(RESULT_CHANNEL_ID)

        if result_channel:
            embed = discord.Embed(
                title="🐉 RANDOMS MATCH RESULT",
                color=discord.Color.purple()
            )

            embed.add_field(name="Winner", value=winner.mention, inline=False)
            embed.add_field(name="Loser", value=loser.mention, inline=False)
            embed.add_field(name="Final Score", value=f"{game['score1']} - {game['score2']}", inline=False)
            embed.add_field(name="Bet", value=f"{bet:,}", inline=False)
            embed.add_field(name="Casino Fee (10%)", value=f"{fee:,}", inline=False)
            embed.add_field(name="Winner Receives", value=f"{payout:,}", inline=False)

            await result_channel.send(embed=embed)

        del randoms_games[channel_id]


async def setup(bot):
    await bot.add_cog(Randoms(bot))
