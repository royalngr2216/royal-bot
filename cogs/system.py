from discord.ext import commands
import discord

from utils.stats import (
    get_profile,
    get_leaderboard
)

from utils.game_state import (
    crack_games,
    randoms_games,
    jackpot_games,
    deathroll_games,
    ongoing_games,
    average_games
)

# ─────────────────────────
# ROLE REWARDS
# ─────────────────────────

ROLE_REWARDS = {
    5: 1478375252290699386,
    20: 1478370330455048192,
    50: 1478380593577332736,
    100: 1478380652020895795,
    200: 1478380725911949313,
    300: 1478380759218917447,
    400: 1478380845193625641,
    500: 1478380890706149397
}


# ─────────────────────────
# RANK SYSTEM
# ─────────────────────────

def get_rank_name(matches):

    ranks = [
        (500, "👑 Royal"),
        (400, "💎 Casino King"),
        (300, "🔥 Elite"),
        (200, "💰 High Roller"),
        (100, "🎲 Addicted"),
        (50, "🃏 Gambler"),
        (20, "⚙️ Grinder"),
        (5, "🌱 Rookie"),
        (0, "👤 Member")
    ]

    for required, name in ranks:

        if matches >= required:
            return name


def get_rank_progress(matches):

    ranks = [
        (0, "Member"),
        (5, "Rookie"),
        (20, "Grinder"),
        (50, "Gambler"),
        (100, "Addicted"),
        (200, "High Roller"),
        (300, "Elite"),
        (400, "Casino King"),
        (500, "Royal")
    ]

    current = (0, "Member")
    next_rank = None

    for i in range(len(ranks)):

        if matches >= ranks[i][0]:

            current = ranks[i]

            if i + 1 < len(ranks):
                next_rank = ranks[i + 1]

    if not next_rank:

        return (
            current[1],
            "MAX",
            100,
            "██████████",
            0
        )

    current_req = current[0]
    next_req = next_rank[0]

    progress = matches - current_req
    total_needed = next_req - current_req

    percent = int(
        (progress / total_needed) * 100
    )

    filled = int(percent / 10)

    bar = (
        "█" * filled
        + "░" * (10 - filled)
    )

    remaining = next_req - matches

    return (
        current[1],
        next_rank[1],
        percent,
        bar,
        remaining
    )


# ─────────────────────────
# UPDATE ROLES
# ─────────────────────────

async def update_roles(member, matches):

    sorted_roles = sorted(
        ROLE_REWARDS.items()
    )

    new_role_id = None

    for required, role_id in sorted_roles:

        if matches >= required:
            new_role_id = role_id

    if not new_role_id:
        return

    guild = member.guild

    new_role = guild.get_role(
        new_role_id
    )

    if not new_role:
        return

    for _, role_id in ROLE_REWARDS.items():

        role = guild.get_role(role_id)

        if role and role in member.roles:

            await member.remove_roles(role)

    await member.add_roles(new_role)


# ─────────────────────────
# HELP VIEW
# ─────────────────────────

class HelpView(discord.ui.View):

    def __init__(self, embeds):

        super().__init__(timeout=120)

        self.embeds = embeds
        self.current_page = 0

    @discord.ui.button(
        label="⬅️",
        style=discord.ButtonStyle.primary
    )
    async def previous(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        self.current_page = (
            self.current_page - 1
        ) % len(self.embeds)

        await interaction.response.edit_message(
            embed=self.embeds[self.current_page],
            view=self
        )

    @discord.ui.button(
        label="➡️",
        style=discord.ButtonStyle.primary
    )
    async def next(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        self.current_page = (
            self.current_page + 1
        ) % len(self.embeds)

        await interaction.response.edit_message(
            embed=self.embeds[self.current_page],
            view=self
        )


# ─────────────────────────
# SYSTEM COG
# ─────────────────────────

class System(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ─────────────────────────
    # HELP
    # ─────────────────────────

    @commands.command(name="help")
    async def help_prefix(self, ctx):

        # PAGE 1

        embed1 = discord.Embed(
            title="🎮 ROYAL ARENA",
            description=(
                "**Game Commands**\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=discord.Color.from_rgb(
                0,
                200,
                255
            )
        )

        embed1.add_field(
            name="🐉 RANDOMS",
            value=(
                "**Command:** `.randoms @user 1/3/5`\n"
                "**Action:** `.pick`\n"
                "**Goal:** Strongest Pokémon wins"
            ),
            inline=False
        )

        embed1.add_field(
            name="💀 DEATHROLL",
            value=(
                "**Command:** `.deathroll @user 1/3/5`\n"
                "**Action:** Roll button\n"
                "**Goal:** Avoid rolling 1"
            ),
            inline=False
        )

        embed1.add_field(
            name="🎯 CRACK",
            value=(
                "**Command:** `.crack @user 1/3/5`\n"
                "**Action:** `.guess number`\n"
                "**Goal:** Guess hidden number"
            ),
            inline=False
        )

        embed1.add_field(
            name="🎰 JACKPOT",
            value=(
                "**Command:** `.jackpot`\n"
                "**Join:** React 🎰\n"
                "**Mode:** Last player survives"
            ),
            inline=False
        )

        embed1.add_field(
            name="📊 AVERAGE",
            value=(
                "**Command:** `.average`\n"
                "**Mode:** Closest to target wins\n"
                "**Twist:** Duplicate numbers lose"
            ),
            inline=False
        )

        embed1.set_footer(
            text="Page 1/2"
        )

        # PAGE 2

        embed2 = discord.Embed(
            title="⚙️ SYSTEM",
            description=(
                "**Utility Commands**\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=discord.Color.orange()
        )

        embed2.add_field(
            name="🛑 STOP",
            value=(
                "**Command:** `.stop`\n"
                "Stops current game"
            ),
            inline=False
        )

        embed2.add_field(
            name="🎖️ PROFILE",
            value=(
                "**Command:** `.profile`\n"
                "Shows player stats"
            ),
            inline=False
        )

        embed2.add_field(
            name="🏆 LEADERBOARD",
            value=(
                "**Command:** `.leaderboard`\n"
                "Shows top players"
            ),
            inline=False
        )

        embed2.add_field(
            name="📡 PING",
            value=(
                "**Command:** `.ping`\n"
                "Shows bot latency"
            ),
            inline=False
        )

        embed2.set_footer(
            text="Page 2/2"
        )

        embeds = [embed1, embed2]

        view = HelpView(embeds)

        await ctx.send(
            embed=embed1,
            view=view
        )

    # ─────────────────────────
    # STOP
    # ─────────────────────────

    @commands.command(name="stop")
    async def stop_prefix(self, ctx):

        channel_id = ctx.channel.id

        stopped = False

        for game_dict in [
            crack_games,
            randoms_games,
            jackpot_games,
            deathroll_games,
            ongoing_games,
            average_games
        ]:

            if channel_id in game_dict:

                del game_dict[channel_id]

                stopped = True

        await ctx.send(
            "🛑 Game stopped."
            if stopped
            else "No active game."
        )

    # ─────────────────────────
    # PROFILE
    # ─────────────────────────

    @commands.command(name="profile")
    async def profile(
        self,
        ctx,
        member: discord.Member = None
    ):

        if member is None:
            member = ctx.author

        stats = get_profile(member.id)

        rank = get_rank_name(
            stats["matches"]
        )

        (
            current_rank,
            next_rank,
            percent,
            bar,
            remaining
        ) = get_rank_progress(
            stats["matches"]
        )

        embed = discord.Embed(
            title=f"🎖️ {member.display_name}",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.add_field(
            name="🏅 Rank",
            value=f"**{rank}**",
            inline=True
        )

        embed.add_field(
            name="🎮 Matches",
            value=f"**{stats['matches']}**",
            inline=True
        )

        embed.add_field(
            name="📊 Winrate",
            value=f"**{stats['winrate']}%**",
            inline=True
        )

        embed.add_field(
            name="🔥 Streak",
            value=f"**{stats.get('streak', 0)}**",
            inline=True
        )

        embed.add_field(
            name="👑 Best Streak",
            value=f"**{stats.get('best_streak', 0)}**",
            inline=True
        )

        embed.add_field(
            name="📈 Progress",
            value=(
                f"**{bar} {percent}%**\n"
                f"Next: **{next_rank}**\n"
                f"Need: **{remaining}**"
            ),
            inline=False
        )

        await ctx.send(embed=embed)

    # ─────────────────────────
    # LEADERBOARD
    # ─────────────────────────

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):

        data = get_leaderboard()

        embed = discord.Embed(
            title="🏆 LEADERBOARD",
            color=discord.Color.gold()
        )

        medals = [
            "🥇",
            "🥈",
            "🥉"
        ]

        desc = ""

        for i, (
            uid,
            matches,
            winrate
        ) in enumerate(data):

            rank = (
                medals[i]
                if i < 3
                else f"#{i+1}"
            )

            desc += (
                f"{rank} <@{uid}>\n"
                f"🎮 **{matches}** matches\n"
                f"📊 **{winrate}%** WR\n\n"
            )

        embed.description = desc

        await ctx.send(embed=embed)

    # ─────────────────────────
    # PING
    # ─────────────────────────

    @commands.command(name="ping")
    async def ping(self, ctx):

        latency = round(
            self.bot.latency * 1000
        )

        embed = discord.Embed(
            description=(
                f"📡 **{latency}ms**"
            ),
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)


# ─────────────────────────
# LOAD COG
# ─────────────────────────

async def setup(bot):

    await bot.add_cog(
        System(bot)
    )
