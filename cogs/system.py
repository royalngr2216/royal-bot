from discord.ext import commands
import discord
from utils.stats import get_profile, get_leaderboard

from utils.game_state import (
    crack_games,
    randoms_games,
    jackpot_games,
    deathroll_games,
    ongoing_games
)

# ─────────────────────────
# Role Rewards System
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
# Rank Name
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


# ─────────────────────────
# Rank Progress System
# ─────────────────────────
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
        return current[1], "MAX", 100, "██████████", 0

    current_req = current[0]
    next_req = next_rank[0]

    progress = matches - current_req
    total_needed = next_req - current_req

    percent = int((progress / total_needed) * 100)

    filled = int(percent / 10)
    bar = "█" * filled + "░" * (10 - filled)

    remaining = next_req - matches

    return current[1], next_rank[1], percent, bar, remaining


# ─────────────────────────
# Role Update System
# ─────────────────────────
async def update_roles(member, matches):
    sorted_roles = sorted(ROLE_REWARDS.items())

    new_role_id = None
    for required, role_id in sorted_roles:
        if matches >= required:
            new_role_id = role_id

    if not new_role_id:
        return

    guild = member.guild
    new_role = guild.get_role(new_role_id)

    if not new_role:
        return

    for _, role_id in ROLE_REWARDS.items():
        role = guild.get_role(role_id)
        if role and role in member.roles:
            await member.remove_roles(role)

    await member.add_roles(new_role)


# ─────────────────────────
# Help UI
# ─────────────────────────
class HelpView(discord.ui.View):
    def __init__(self, embeds):
        super().__init__(timeout=120)
        self.embeds = embeds
        self.current_page = 0

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page - 1) % len(self.embeds)
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page + 1) % len(self.embeds)
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)


# ─────────────────────────
# System Cog
# ─────────────────────────
class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_prefix(self, ctx):

    # ───────────── PAGE 1 — GAMES
    embed1 = discord.Embed(
        title="🎮 Royal Arena — Games",
        description="Play exciting betting games with others\n━━━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.from_rgb(0, 200, 255)
    )

    embed1.add_field(
        name="🪙 Flip",
        value="Quick coin toss (50/50)\nUsage: `.flip`\nExample: `.flip`",
        inline=False
    )

    embed1.add_field(
        name="🐉 Randoms",
        value="Pick random fighters → strongest wins\nUsage: `.randoms @user BO amount`\nExample: `.randoms @royalngr 3 500k`",
        inline=False
    )

    embed1.add_field(
        name="💀 Deathroll",
        value="Roll until someone hits 1\nUsage: `.deathroll @user BO amount`\nExample: `.deathroll @user 5 1m`",
        inline=False
    )

    embed1.add_field(
        name="🔢 Crack",
        value="Guess number closest to target\nUsage: `.crack @user BO amount`\nExample: `.crack @user 3 500k`",
        inline=False
    )

    embed1.add_field(
        name="🎰 Jackpot",
        value="Join pool → random winner\nUsage: `.jackpot`",
        inline=False
    )

    embed1.set_footer(text="Page 1/2 • Games")

    # ───────────── PAGE 2 — SYSTEM
    embed2 = discord.Embed(
        title="⚙️ Royal Arena — System",
        description="Stats, ranking & utilities\n━━━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.from_rgb(255, 170, 0)
    )

    embed2.add_field(
        name="🎖️ Profile",
        value="Check your stats & rank\nUsage: `.profile`",
        inline=False
    )

    embed2.add_field(
        name="🏆 Leaderboard",
        value="Top players ranking\nUsage: `.leaderboard`",
        inline=False
    )

    embed2.add_field(
        name="🛑 Stop",
        value="Stop ongoing game\nUsage: `.stop`",
        inline=False
    )

    embed2.add_field(
        name="📡 Ping",
        value="Check bot latency\nUsage: `.ping`",
        inline=False
    )

    embed2.set_footer(text="Page 2/2 • System")

    await ctx.send(embed=embed1, view=HelpView([embed1, embed2]))

    @commands.command(name="stop")
    async def stop_prefix(self, ctx):

        channel_id = ctx.channel.id
        stopped = False

        for game_dict in [crack_games, randoms_games, jackpot_games, deathroll_games, ongoing_games]:
            if channel_id in game_dict:
                del game_dict[channel_id]
                stopped = True

        await ctx.send("🛑 Stopped" if stopped else "No active games.")

    @commands.command(name="profile")
    async def profile(self, ctx, member: discord.Member = None):

        if member is None:
            member = ctx.author

        stats = get_profile(member.id)
        rank = get_rank_name(stats["matches"])
        current_rank, next_rank, percent, bar, remaining = get_rank_progress(stats["matches"])

        embed = discord.Embed(
            title="🎖️ Player Profile",
            description=f"{member.display_name}",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="🏅 Rank", value=rank, inline=True)
        embed.add_field(name="🎲 Bets", value=stats["matches"], inline=True)
        embed.add_field(name="💀 Losses", value=stats["losses"], inline=True)

        embed.add_field(
            name="📊 Progress",
            value=f"{bar} {percent}%\n⬆️ Next: {next_rank}\n📌 Need: {remaining} bets",
            inline=False
        )

        embed.add_field(name="📊 Winrate", value=f"{stats['winrate']}%", inline=True)
        embed.add_field(name="🔥 Streak", value=stats.get("streak", 0), inline=True)
        embed.add_field(name="🏅 Best", value=stats.get("best_streak", 0), inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):

    data = get_leaderboard()

    embed = discord.Embed(
        title="🏆 Player Leaderboard",
        description="Top Players by Total Bets\n━━━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.gold()
    )

    medals = ["🥇", "🥈", "🥉"]

    desc = ""

    for i, (uid, matches, winrate) in enumerate(data):

        if i < 3:
            rank = medals[i]
        else:
            rank = f"#{i+1}"

        desc += (
            f"{rank} <@{uid}>\n"
            f"🎲 Bets: {matches} | 📊 Win Rate: {winrate}%\n\n"
        )

    embed.description += f"\n{desc}"

    await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(System(bot))
