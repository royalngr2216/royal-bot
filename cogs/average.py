import discord
from discord.ext import commands
import asyncio

# Replace this with your actual import path if needed
from utils.game_state import average_games


# ─────────────────────────────────────────────────────────
# UI MODAL: NUMBER INPUT
# ─────────────────────────────────────────────────────────
class PickNumberModal(discord.ui.Modal, title="🎯 Lock Your Guess"):
    """Opens a native text input pop-up for the user to submit their number."""
    
    number_input = discord.ui.TextInput(
        label="Choose a number (0 - 1000)",
        placeholder="Enter your strategic guess here...",
        min_length=1,
        max_length=4,
        required=True
    )

    def __init__(self, game_cog, guild_id):
        super().__init__()
        self.game_cog = game_cog
        self.guild_id = guild_id

    async def on_submit(self, interaction: discord.Interaction):
        if self.guild_id not in self.game_cog.active_games:
            return await interaction.response.send_message("❌ This game has already ended.", ephemeral=True)

        game = self.game_cog.active_games[self.guild_id]

        if interaction.user not in game["players"]:
            return await interaction.response.send_message("❌ You aren't signed up for this match!", ephemeral=True)

        try:
            val = int(self.number_input.value)
        except ValueError:
            return await interaction.response.send_message("❌ Please enter a valid integer.", ephemeral=True)

        if val < 0 or val > 1000:
            return await interaction.response.send_message("❌ Your number must be between 0 and 1000.", ephemeral=True)

        game["numbers"][interaction.user.id] = val
        await interaction.response.send_message(f"🔒 Locked in: **{val}**", ephemeral=True)

        await self.game_cog.update_submission_board(self.guild_id)


# ─────────────────────────────────────────────────────────
# UI VIEW: ACTIVE INPUT BUTTON
# ─────────────────────────────────────────────────────────
class GameControlView(discord.ui.View):
    """Holds the button that triggers the Modal pop-up."""
    
    def __init__(self, game_cog, guild_id):
        super().__init__(timeout=None)
        self.game_cog = game_cog
        self.guild_id = guild_id

    @discord.ui.button(label="Submit Number", style=discord.ButtonStyle.primary, emoji="🎲")
    async def submit_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PickNumberModal(self.game_cog, self.guild_id)
        await interaction.response.send_modal(modal)


# ─────────────────────────────────────────────────────────
# UI VIEW: LOBBY SIGN-UP BUTTON
# ─────────────────────────────────────────────────────────
class LobbyView(discord.ui.View):
    """Handles the sign-up phase using UI Buttons instead of classic reactions."""
    
    def __init__(self):
        super().__init__(timeout=20.0)
        self.players = []

    @discord.ui.button(label="Join Arena", style=discord.ButtonStyle.success, emoji="🎮")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            return await interaction.response.send_message("You are already in the queue!", ephemeral=True)
        
        self.players.append(interaction.user)
        await interaction.response.send_message("⚔️ Joined the game!", ephemeral=True)


# ─────────────────────────────────────────────────────────
# MAIN COG (UPDATED TO PREFIX ROUTING)
# ─────────────────────────────────────────────────────────
class AverageGame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.active_games = average_games

    # ──────────────────────────────────────────
    # PREFIX COMMAND START (Triggers with .average)
    # ──────────────────────────────────────────
    @commands.command(name="average")
    async def average(self, ctx: commands.Context):
        guild = ctx.guild
        if not guild:
            return

        if guild.id in self.active_games:
            return await ctx.send("❌ An Average game is already running here.")

        # Build Clean Modern Lobby Embed
        lobby_embed = discord.Embed(
            title="🎯 Average Arena",
            description="Press the button below to join the match.\n\n🏆 Goal: **Closest to [Average × 0.8] wins.**",
            color=0x5865F2
        )
        lobby_embed.add_field(
            name="📌 Rules",
            value="• Submit a number from **0 to 1000** via popup modal\n• All inputs are hidden until judgment\n• Simultaneous turns: no more waiting around!",
            inline=False
        )
        lobby_embed.set_footer(text="Lobby closing in 20 seconds...")

        view = LobbyView()
        lobby_msg = await ctx.send(embed=lobby_embed, view=view)

        # Wait for lobby timeout (20s)
        await view.wait()

        # Deduplicate list safely
        players = list(dict.fromkeys(view.players))

        if len(players) < 2:
            # Disable buttons on the lobby message so it's clean
            await lobby_msg.edit(view=None)
            return await ctx.send("❌ Game cancelled: Need at least 2 players to start.")

        # Instantiate Game Session Map
        game = {
            "players": players,
            "numbers": {},
            "channel": ctx.channel,
            "board_msg": None
        }
        self.active_games[guild.id] = game

        # Announce Match Start
        start_embed = discord.Embed(
            title="🏁 Match Commenced!",
            description="Click **Submit Number** below to securely pass your number.",
            color=0x57F287
        )
        
        player_status = "\n".join([f"⏳ {p.mention} — *Thinking...*" for p in players])
        start_embed.add_field(name="📋 Roster Status", value=player_status, inline=False)

        control_view = GameControlView(self, guild.id)
        board_msg = await ctx.send(embed=start_embed, view=control_view)
        
        game["board_msg"] = board_msg

    # ─────────────────────────
    # LIVE STATUS UPDATER
    # ─────────────────────────
    async def update_submission_board(self, guild_id):
        game = self.active_games.get(guild_id)
        if not game or not game["board_msg"]:
            return

        players = game["players"]
        numbers = game["numbers"]

        status_lines = []
        for p in players:
            if p.id in numbers:
                status_lines.append(f"✅ {p.mention} — **Locked In**")
            else:
                status_lines.append(f"⏳ {p.mention} — *Thinking...*")

        status_text = "\n".join(status_lines)

        updated_embed = discord.Embed(
            title="🏁 Match Active",
            description="Click **Submit Number** below to securely pass your number.",
            color=0xFAA61A
        )
        updated_embed.add_field(name="📋 Roster Status", value=status_text, inline=False)
        
        await game["board_msg"].edit(embed=updated_embed)

        if len(numbers) == len(players):
            await asyncio.sleep(1.5)
            await self.finish_game(guild_id)

    # ─────────────────────────
    # JUDGMENT & EVALUATION
    # ─────────────────────────
    async def finish_game(self, guild_id):
        game = self.active_games[guild_id]
        players = game["players"]
        numbers = game["numbers"]
        board_msg = game["board_msg"]

        await board_msg.edit(view=None)

        values = list(numbers.values())
        average = sum(values) / len(values)
        target = average * 0.8

        distances = {p.id: abs(numbers[p.id] - target) for p in players}
        closest = min(distances.values())

        winners = [p for p in players if distances[p.id] == closest]

        reveal = "\n".join([f"> {p.mention} → `{numbers[p.id]}`" for p in players])

        results_embed = discord.Embed(
            title="📊 Game Results Summary",
            color=0xEB459E
        )
        results_embed.add_field(name="🎲 Revealing Choices", value=reveal, inline=False)
        results_embed.add_field(
            name="🧮 Calculations Summary",
            value=f"> Average Selection: `{average:.2f}`\n> Target Vector ($Average \\times 0.8$): `{target:.2f}`",
            inline=False
        )

        if len(winners) > 1:
            draw_mentions = " ".join([w.mention for w in winners])
            results_embed.add_field(
                name="🤝 Draw Verdict",
                value=f"{draw_mentions}\nEqually closest distance to target!",
                inline=False
            )
        else:
            results_embed.add_field(
                name="🏆 Apex Victor",
                value=f"{winners[0].mention}\nAbsolute closest choice to target `{target:.2f}`!",
                inline=False
            )

        results_embed.set_footer(text="Average Arena Engine")
        await game["channel"].send(embed=results_embed)

        del self.active_games[guild_id]


async def setup(bot):
    await bot.add_cog(AverageGame(bot))
    
