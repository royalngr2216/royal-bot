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

    # PREFIX HELP COMMAND
    @commands.command(name="help")
    async def help_prefix(self, ctx):

        # ───────────────────────── PAGE 1 (Games)
        embed1 = discord.Embed(
            title="🎮  ROYAL ARENA",
            description="Navigate using ⬅️ ➡️ buttons\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            color=discord.Color.from_rgb(0, 200, 255)
        )

        embed1.add_field(
            name="━━━━━━━━━━ 🪙 FLIP ━━━━━━━━━━",
            value=(
                "```yaml\n"
                "Command : .flip\n"
                "Type    : Coin Flipping Game\n"
                "Win     : 50 / 50 chance for Everyone!\n"
                "```"
            ),
            inline=False
        )

        embed1.add_field(
            name="━━━━━━━━━━ 🐉 RANDOMS ━━━━━━━━━━",
            value=(
                "```yaml\n"
                "Command : .randoms @user\n"
                "Action  : Both users type .pick\n"
                "Result  : The Strongest Wins\n"
                "```"
            ),
            inline=False
        )

        embed1.add_field(
            name="━━━━━━━━━━ 💀 DEATHROLL ━━━━━━━━━━",
            value=(
                "```yaml\n"
                "Command : .deathroll @user (1/3/5) bet\n"
                "Example : .deathroll @user 3 1m\n"
                "Mode    : Whoever gets 1 loses the Match\n"
                "```"
            ),
            inline=False
        )

        embed1.add_field(
            name="━━━━━━━━━━ 🔢 CRACK ━━━━━━━━━━",
            value=(
                "```yaml\n"
                "Command : .crack @user (1/3/5) bet\n"
                "Action  : Both users type .guess\n"
                "Goal    : Closest guess wins\n"
                "```"
            ),
            inline=False
        )

        embed1.add_field(
            name="━━━━━━━━━━ 🎰 JACKPOT ━━━━━━━━━━",
            value=(
                "```yaml\n"
                "Command : .jackpot\n"
                "Join    : React 🎰\n"
                "Mode    : Random Elimination\n"
                "```"
            ),
            inline=False
        )

        embed1.set_footer(text="Page 1/2 • Games")

        # ───────────────────────── PAGE 2 (System)
        embed2 = discord.Embed(
            title="⚙️ System",
            description="Administrative & Utility Commands\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            color=discord.Color.from_rgb(255, 170, 0)
        )

        embed2.add_field(
            name="━━━━━━━━━━ 🛑 STOP ━━━━━━━━━━",
            value=(
                "```yaml\n"
                "Command : .stop\n"
                "Effect  : Stops all active games in this channel\n"
                "Scope   : Only affects current channel\n"
                "```"
            ),
            inline=False
        )

        embed2.add_field(
            name="━━━━━━━━━━ 📡 PING ━━━━━━━━━━",
            value=(
                "```yaml\n"
                "Command : .ping\n"
                "Effect  : Shows bot latency\n"
                "```"
            ),
            inline=False
        )

        embed2.add_field(
            name="━━━━━━━━━━ 🎖️ PROFILE ━━━━━━━━━━",
            value=(
                "```yaml\n"
                "Command : .profile @user(optional)\n"
                "Shows   : Player stats & win ratio\n"
                "```"
            ),
            inline=False
        )

        embed2.add_field(
            name="━━━━━━━━━━ 🏆 LEADERBOARD ━━━━━━━━━━",
            value=(
                "```yaml\n"
                "Command : .leaderboard\n"
                "Shows   : Top players by total bets\n"
                "```"
            ),
            inline=False
        )

        embed2.set_footer(text="Page 2/2 • System")

        embeds = [embed1, embed2]
        view = HelpView(embeds)

        await ctx.send(embed=embed1, view=view)

    # PREFIX STOP COMMAND
    @commands.command(name="stop")
    async def stop_prefix(self, ctx):

        channel_id = ctx.channel.id
        stopped = False

        for game_dict in [
            crack_games,
            randoms_games,
            jackpot_games,
            deathroll_games,
            ongoing_games
        ]:
            if channel_id in game_dict:
                del game_dict[channel_id]
                stopped = True

        if stopped:
            await ctx.send("🛑 All games in this channel have been stopped.")
        else:
            await ctx.send("No active games in this channel.")

    @commands.command(name="profile")
    async def profile(self, ctx, member: discord.Member = None):

        if member is None:
            member = ctx.author

        stats = get_profile(member.id)

        if not stats:
            await ctx.send("This user has no recorded matches.")
            return

        embed = discord.Embed(
            title="🎖️ Player Profile",
            description=f"Stats for **{member.display_name}**",
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="🎲 Total Bets", value=stats["matches"], inline=True)
        embed.add_field(name="🏆 Wins", value=stats["wins"], inline=True)
        embed.add_field(name="💀 Losses", value=stats["losses"], inline=True)
        embed.add_field(name="📊 Win Rate", value=f"{stats['winrate']}%", inline=False)
        embed.add_field(name="💰 Total Won", value=f"{stats['total_won']:,}", inline=True)
        embed.add_field(name="📉 Total Lost", value=f"{stats['total_lost']:,}", inline=True)

        embed.set_footer(text="Game Arena Competitive Stats")

        await ctx.send(embed=embed)

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):

        leaderboard_data = get_leaderboard()

        if not leaderboard_data:
            await ctx.send("No players recorded yet.")
            return

        embed = discord.Embed(
            title="🏆 Player Leaderboard",
            description="Top Players by Total Bets\n",
            color=discord.Color.blue()
        )

        medals = ["🥇", "🥈", "🥉"]

        for index, (user_id, matches, winrate) in enumerate(leaderboard_data):

            name = f"<@{user_id}>"

            if index < 3:
                rank_icon = medals[index]
            else:
                rank_icon = f"`#{index + 1}`"

            embed.description += (
                f"{rank_icon} {name}\n"
                f"🎲 Bets: {matches} | 📊 Win Rate: {winrate}%\n\n"
            )
            
        embed.set_footer(text="Only official completed matches are counted")

        await ctx.send(embed=embed)

@commands.command(name="rewards")
async def rewards(self, ctx):

    embed = discord.Embed(
        title="🎖️ Royal Arena Rank Rewards",
        description="Progress through levels and unlock exclusive roles.\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.from_rgb(255, 215, 0)
    )

    embed.add_field(
        name="👑 Royal",
        value="`Level 500+`",
        inline=False
    )

    embed.add_field(
        name="💎 Casino King",
        value="`Level 400+`",
        inline=False
    )

    embed.add_field(
        name="🔥 Elite",
        value="`Level 300+`",
        inline=False
    )

    embed.add_field(
        name="💰 High Roller",
        value="`Level 200+`",
        inline=False
    )

    embed.add_field(
        name="🎲 Addicted",
        value="`Level 100+`",
        inline=False
    )

    embed.add_field(
        name="🃏 Gambler",
        value="`Level 50+`",
        inline=False
    )

    embed.add_field(
        name="⚙️ Grinder",
        value="`Level 20+`",
        inline=False
    )

    embed.add_field(
        name="🌱 Rookie",
        value="`Level 5+`",
        inline=False
    )

    embed.add_field(
        name="👤 Member",
        value="Default role",
        inline=False
    )

    embed.set_footer(text="Climb the ranks by playing games and increasing your level")

    await ctx.send(embed=embed)
    
async def setup(bot):
    await bot.add_cog(System(bot))
