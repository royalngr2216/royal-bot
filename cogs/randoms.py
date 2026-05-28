from discord.ext import commands
import random
import discord

from data.pokemon import POKEMON_LIST

from utils.stats import (
    record_win,
    record_loss,
    get_profile
)

from cogs.system import update_roles

from utils.game_state import randoms_games


SPECIAL_PLAYERS = {
    1287545546231255092,
    711959035238285443
}

SORTED_POKEMON = sorted(
    POKEMON_LIST,
    key=lambda p: p.total_stats,
    reverse=True
)

SPECIAL_POOL = [
    p for p in POKEMON_LIST
    if 450 <= p.total_stats <= 780
]


class Randoms(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ─────────────────────────
    # START MATCH
    # ─────────────────────────

    @commands.command(name="randoms")
    async def randoms(
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
                "`.randoms @user 3`"
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

        if ctx.channel.id in randoms_games:

            await ctx.send(
                "A randoms match is already active in this channel."
            )

            return

        wins_required = (bo // 2) + 1

        randoms_games[ctx.channel.id] = {

            "player1": ctx.author,
            "player2": opponent,

            "bo": bo,

            "wins_required": wins_required,

            "score1": 0,
            "score2": 0,

            "picks": {}
        }

        await ctx.send(

            f"🐉 Randoms — BO{bo} Started!\n\n"

            f"{ctx.author.mention} ⚔️ "
            f"{opponent.mention}\n\n"

            f"🏆 First to "
            f"{wins_required} wins.\n\n"

            f"Both players use `.pick`"

        )

    # ─────────────────────────
    # PICK COMMAND
    # ─────────────────────────

    @commands.command(name="pick")
    async def pick(self, ctx):

        if ctx.channel.id not in randoms_games:

            await ctx.send(
                "No active randoms match."
            )

            return

        game = randoms_games[ctx.channel.id]

        if ctx.author not in [

            game["player1"],
            game["player2"]

        ]:

            await ctx.send(
                "You are not part of this match."
            )

            return

        if ctx.author in game["picks"]:

            await ctx.send(
                "You already picked this round."
            )

            return

        # SPECIAL PLAYER LOGIC
        if ctx.author.id in SPECIAL_PLAYERS:

            roll = random.randint(1, 100)

            if roll <= 20:

                pool = [
                    p for p in POKEMON_LIST
                    if 450 <= p.total_stats <= 500
                ]

            elif roll <= 35:

                pool = [
                    p for p in POKEMON_LIST
                    if 500 < p.total_stats <= 530
                ]

            elif roll <= 80:

                pool = [
                    p for p in POKEMON_LIST
                    if 530 < p.total_stats <= 580
                ]

            elif roll <= 92:

                pool = [
                    p for p in POKEMON_LIST
                    if 570 < p.total_stats <= 680
                ]

            else:

                pool = [
                    p for p in POKEMON_LIST
                    if 680 < p.total_stats <= 780
                ]

            if not pool:
                pool = SPECIAL_POOL

            pokemon = random.choice(pool)

        else:

            pokemon = random.choice(
                POKEMON_LIST
            )

        game["picks"][ctx.author] = pokemon

        clean_name = (

            pokemon.name.lower()
            .replace(" ", "")
            .replace(".", "")
            .replace("'", "")

        )

        gif_url = (
            "https://play.pokemonshowdown.com/"
            f"sprites/xyani/{clean_name}.gif"
        )

        # EMBED COLOR
        if pokemon.total_stats < 400:

            embed_color = discord.Colour.green()

        elif pokemon.total_stats < 500:

            embed_color = discord.Colour.blue()

        else:

            embed_color = discord.Colour.red()

        embed = discord.Embed(

            title=(
                f"{ctx.author.display_name} "
                f"picked {pokemon.name}"
            ),

            color=embed_color
        )

        embed.set_image(
            url=gif_url
        )

        embed.add_field(
            name="HP",
            value=pokemon.hp,
            inline=True
        )

        embed.add_field(
            name="Attack",
            value=pokemon.attack,
            inline=True
        )

        embed.add_field(
            name="Defense",
            value=pokemon.defense,
            inline=True
        )

        embed.add_field(
            name="Sp. Attack",
            value=pokemon.sp_attack,
            inline=True
        )

        embed.add_field(
            name="Sp. Defense",
            value=pokemon.sp_defense,
            inline=True
        )

        embed.add_field(
            name="Speed",
            value=pokemon.speed,
            inline=True
        )

        embed.add_field(
            name="Total Base Power",
            value=pokemon.total_stats,
            inline=False
        )

        await ctx.send(embed=embed)

        # BOTH PICKED
        if len(game["picks"]) == 2:

            await self.resolve_round(
                ctx.channel.id
            )

    # ─────────────────────────
    # RESOLVE ROUND
    # ─────────────────────────

    async def resolve_round(
        self,
        channel_id
    ):

        game = randoms_games[channel_id]

        p1 = game["player1"]
        p2 = game["player2"]

        poke1 = game["picks"][p1]
        poke2 = game["picks"][p2]

        channel = self.bot.get_channel(
            channel_id
        )

        # WINNER
        if poke1.total_stats > poke2.total_stats:

            game["score1"] += 1

            winner = p1

        elif poke2.total_stats > poke1.total_stats:

            game["score2"] += 1

            winner = p2

        else:

            winner = None

        # ROUND RESULT
        if winner:

            await channel.send(

                f"🏆 {winner.mention} "
                f"wins the round!\n\n"

                f"📊 Score:\n"
                f"**{game['score1']}**"
                f" - "
                f"**{game['score2']}**"

            )

        else:

            await channel.send(
                "🤝 Round tied!"
            )

        # RESET PICKS
        game["picks"] = {}

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
                channel_id
            )

    # ─────────────────────────
    # END MATCH
    # ─────────────────────────

    async def end_match(
        self,
        channel_id
    ):

        game = randoms_games[channel_id]

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
            title="🐉 RANDOMS RESULT",
            color=discord.Color.purple()
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
        del randoms_games[channel_id]


async def setup(bot):

    await bot.add_cog(
        Randoms(bot)
    )
