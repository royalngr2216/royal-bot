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
    5: 1478375252290699386,     # Rookie
    20: 1478370330455048192,    # Grinder
    50: 1478380593577332736,    # Gambler
    100: 1478380652020895795,   # Addicted
    200: 1478380725911949313,   # High Roller
    300: 1478380759218917447,   # Elite
    400: 1478380845193625641,   # Casino King
    500: 1478380890706149397    # Royal
}

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

    # Remove old roles
    for _, role_id in ROLE_REWARDS.items():
        role = guild.get_role(role_id)
        if role and role in member.roles:
            await member.remove_roles(role)

    # Add new role
    await member.add_roles(new_role)


# ─────────────────────────────────────────────
# Pagination View
# ─────────────────────────────────────────────
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


class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_prefix(self, ctx):

        embed1 = discord.Embed(
            title="🎮  ROYAL ARENA",
            description="Navigate using ⬅️ ➡️ buttons\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            color=discord.Color.from_rgb(0, 200, 255)
        )

        embed1.add_field(
            name="━━━━━━━━━━ 🪙 FLIP ━━━━━━━━━━",
            value="```yaml\nCommand : .flip\nType : Coin Flipping Game\nWin : 50 / 50 chance\n```",
            inline=False
        )

        embed1.add_field(
            name="━━━━━━━━━━ 🐉 RANDOMS ━━━━━━━━━━",
            value="```yaml\nCommand : .randoms @user\nAction : .pick\nResult : Strongest Wins\n```",
            inline=False
        )

        embed1.add_field(
            name="━━━━━━━━━━ 💀 DEATHROLL ━━━━━━━━━━",
            value="```yaml\nCommand : .deathroll @user\nMode : Whoever gets 1 loses\n```",
            inline=False
        )

        embed1.add_field(
            name="━━━━━━━━━━ 🔢 CRACK ━━━━━━━━━━",
            value="```yaml\nCommand : .crack @user\nAction : .guess\nGoal : Closest wins\n```",
            inline=False
        )

        embed1.add_field(
            name="━━━━━━━━━━ 🎰 JACKPOT ━━━━━━━━━━",
            value="```yaml\nCommand : .jackpot\nJoin : React 🎰\nMode : Random\n```",
            inline=False
        )

        embed1.set_footer(text="Page 1/2 • Games")

        embed2 = discord.Embed(
            title="⚙️ System",
            description="Commands\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            color=discord.Color.from_rgb(255, 170, 0)
        )

        embed2.add_field(name="🛑 STOP", value="`.stop`", inline=False)
        embed2.add_field(name="📡 PING", value="`.ping`", inline=False)
        embed2.add_field(name="🎖️ PROFILE", value="`.profile`", inline=False)
        embed2.add_field(name="🏆 LEADERBOARD", value="`.leaderboard`", inline=False)

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

        embed = discord.Embed(
            title="🎖️ Player Profile",
            description=f"{member.display_name}",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="🎲 Bets", value=stats["matches"], inline=True)
        embed.add_field(name="💀 Losses", value=stats["losses"], inline=True)
        embed.add_field(name="📊 Winrate", value=f"{stats['winrate']}%", inline=False)
        embed.add_field(name="🔥 Streak", value=stats.get("streak", 0), inline=True)
        embed.add_field(name="🏅 Best", value=stats.get("best_streak", 0), inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):

        data = get_leaderboard()

        embed = discord.Embed(title="🏆 Leaderboard", color=discord.Color.blue())

        for i, (uid, matches, winrate) in enumerate(data):
            embed.description = (embed.description or "") + f"{i+1}. <@{uid}> — {matches} bets ({winrate}%)\n"

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(System(bot))
