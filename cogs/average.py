import discord
from discord.ext import commands
from discord import app_commands
import asyncio

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
        # Validate that the game is still running
        if self.guild_id not in self.game_cog.active_games:
            return await interaction.response.send_message("❌ This game has already ended.", ephemeral=True)

        game = self.game_cog.active_games[self.guild_id]

        # Check if the user is an active participant
        if interaction.user not in game["players"]:
            return await interaction.response.send_message("❌ You aren't signed up for this match!", ephemeral=True)

        # Validate input type
        try:
            val = int(self.number_input.value)
        except ValueError:
            return await interaction.response.send_message("❌ Please enter a valid integer.", ephemeral=True)

        # Validate boundaries
        if val < 0 or val > 1000:
            return await interaction.response.send_message("❌ Your number must be between 0 and 1000.", ephemeral=True)

        # Save guess
        game["numbers"][interaction.user.id] = val
        await interaction.response.send_message(f"🔒 Locked in: **{val}**", ephemeral=True)

        # Update the main tracking board
        await self.game_cog.update_submission_board(self.guild_id)


# ─────────────────────────────────────────────────────────
# UI VIEW: ACTIVE INPUT BUTTON
# ─────────────────────────────────────────────────────────
class GameControlView(discord.ui.View):
    """Holds the button that triggers the Modal pop-up."""
    
    def __init__(self, game_cog, guild_id):
        super().__init__(timeout=None) # Keeps persistent until game manually finishes
        self.game_cog = game_cog
        self.guild_id = guild_id

    @discord.ui.button(label="Submit Number", style=discord.ButtonStyle.primary, emoji="🎲")
    async def submit_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Open the pop-up modal for input
        modal = PickNumberModal(self.game_cog, self.guild_id)
        await interaction.response.send_modal(modal)


# ─────────────────────────────────────────────────────────
# UI VIEW: LOBBY SIGN-UP BUTTON
# ─────────────────────────────────────────────────────────
class LobbyView(discord.ui.View):
    """Handles the sign-up phase using UI Buttons instead of classic reactions."""
    
    def __init__(self):
        super().__init__(timeout=20.0) # 20 second registration phase
        self.players = []

    @discord.ui.button(label="Join Arena", style=discord.ButtonStyle.success, emoji="🎮")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.players:
            return await interaction.response.send_message("You are already in the queue!", ephemeral=True)
        
        self.players.append(interaction.user)
        await interaction.response.send_message("⚔️ Joined the game!", ephemeral=True)


# ─────────────────────────────────────────────────────────
# MAIN COG
# ─────────────────────────────────────────────────────────
class AverageGame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.active_games = average_games

    # ─────────────────────────
    # SLASH COMMAND: START GAME
    # ─────────────────────────
    @app_commands.command(name="average", description="Launch an Average Arena game lobby.")
    async def average(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            return

        if guild.id in self.active_games:
            return await interaction.response.send_message("❌ An Average game is already running here.", ephemeral=True)

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
        await interaction.response.send_message(embed=lobby_embed, view=view)

        # Wait for lobby timeout (20s)
        await view.wait()

        # Deduplicate list safely
        players = list(dict.fromkeys(view.players))

        if len(players) < 2:
            return await interaction.channel.send("❌ Game cancelled: Need at least 2 players to start.")

        # Instantiate Game Session Map
        game = {
            "players": players,
            "numbers": {},
            "channel": interaction.channel,
            "board_msg": None  # Dynamic live status update tracking
        }
        self.active_games[guild.id] = game

        # Announce Match Start
        start_embed = discord.Embed(
            title="🏁 Match Commenced!",
            description="Click **Submit Number** below to securely pass your number.",
            color=0x57F287
        )
        
        # Build progress visualizer
        player_status = "\n".join([f"⏳ {p.mention} — *Thinking...*" for p in players])
        start_embed.add_field(name="📋 Roster Status", value=player_status, inline=False)

        control_view = GameControlView(self, guild.id)
        board_msg = await interaction.channel.send(embed=start_embed, view=control_view)
        
        # Save message pointer for dynamic refreshing
        game["board_msg"] = board_msg

    # ─────────────────────────
    # LIVE STATUS UPDATER
    # ─────────────────────────
    async def update_submission_board(self, guild_id):
        """Refreshes the message frame to show who has lock/unlocked their entry."""
        game = self.active_games.get(guild_id)
        if not game or not game["board_msg"]:
            return

        players = game["players"]
        numbers = game["numbers"]

        # Build dynamic roster state text
        status_lines = []
        for p in players:
            if p.id in numbers:
                status_lines.append(f"✅ {p.mention} — **Locked In**")
            else:
                status_lines.append(f"⏳ {p.mention} — *Thinking...*")

        status_text = "\n".join(status_lines)

        # Edit frame update
        updated_embed = discord.Embed(
            title="🏁 Match Active",
            description="Click **Submit Number** below to securely pass your number.",
            color=0xFAA61A
        )
        updated_embed.add_field(name="📋 Roster Status", value=status_text, inline=False)
        
        await game["board_msg"].edit(embed=updated_embed)

        # All players done? Trigger resolution routine immediately
        if len(numbers) == len(players):
            # Short aesthetic sleep so players see all greens checked
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

        # Disable the interactive view button on the board
        await board_msg.edit(view=None)

        # Computations
        values = list(numbers.values())
        average = sum(values) / len(values)
        target = average * 0.8

        distances = {p.id: abs(numbers[p.id] - target) for p in players}
        closest = min(distances.values())

        winners = [p for p in players if distances[p.id] == closest]

        # Compile Reveals
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

        # Tie/Draw State
        if len(winners) > 1:
            draw_mentions = " ".join([w.mention for w in winners])
            results_embed.add_field(
                name="🤝 Draw Verdict",
                value=f"{draw_mentions}\nEqually closest distance to target!",
                inline=False
            )
        # Solo Winner State
        else:
            results_embed.add_field(
                name="🏆 Apex Victor",
                value=f"{winners[0].mention}\nAbsolute closest choice to target `{target:.2f}`!",
                inline=False
            )

        results_embed.set_footer(text="Average Arena Engine")
        await game["channel"].send(embed=results_embed)

        # Drop reference session state
        del self.active_games[guild_id]


async def setup(bot):
    await bot.add_cog(AverageGame(bot))
    f"✅ {interaction.user.mention} has chosen their number."
        )

        game["current"] += 1

        # Next player
        if game["current"] < len(game["players"]):

            next_player = game["players"][game["current"]]

            embed = discord.Embed(
                title="🔢 Next Turn",
                description=(
                    f"{next_player.mention}, choose your number using:\n"
                    f"`/pick number:<your number>`"
                ),
                color=discord.Color.orange()
            )

            await game["channel"].send(embed=embed)

        else:
            await self.finish_game(guild.id)

    # ─────────────────────────
    # FINISH GAME
    # ─────────────────────────

    async def finish_game(self, guild_id):

        game = self.active_games[guild_id]

        players = game["players"]
        numbers = game["numbers"]
        channel = game["channel"]

        values = list(numbers.values())

        average = sum(values) / len(values)

        target = average * 0.8

        distances = {}

        for player in players:

            player_number = numbers[player.id]

            distances[player.id] = abs(
                player_number - target
            )

        min_distance = min(distances.values())

        winners = []

        for player in players:

            if distances[player.id] == min_distance:
                winners.append(player)

        result_embed = discord.Embed(
            title="📊 Average Game Results",
            color=discord.Color.purple()
        )

        number_text = ""

        for player in players:

            number_text += (
                f"{player.mention} → **{numbers[player.id]}**\n"
            )

        result_embed.add_field(
            name="🎲 Chosen Numbers",
            value=number_text,
            inline=False
        )

        result_embed.add_field(
            name="📈 Calculations",
            value=(
                f"Average = **{average:.2f}**\n"
                f"Average × 0.8 = **{target:.2f}**"
            ),
            inline=False
        )

        # DRAW
        if len(winners) > 1:

            winner_mentions = ", ".join(
                [w.mention for w in winners]
            )

            result_embed.add_field(
                name="🤝 Draw!",
                value=(
                    f"Closest distance matched between:\n"
                    f"{winner_mentions}"
                ),
                inline=False
            )

        # SINGLE WINNER
        else:

            winner = winners[0]

            result_embed.add_field(
                name="🏆 Winner",
                value=f"{winner.mention} wins!",
                inline=False
            )

        await channel.send(embed=result_embed)

        del self.active_games[guild_id]


# ─────────────────────────
# LOAD COG
# ─────────────────────────

async def setup(bot):
    await bot.add_cog(AverageGame(bot))
