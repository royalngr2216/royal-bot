import discord
from discord.ext import commands
import asyncio
import random

from utils.game_state import average_games


# ─────────────────────────
# NUMBER INPUT MODAL
# ─────────────────────────

class PickNumberModal(discord.ui.Modal):

    def __init__(self, game_cog, guild_id):

        super().__init__(
            title="🎯 Lock Your Number"
        )

        self.game_cog = game_cog
        self.guild_id = guild_id

        self.number_input = discord.ui.TextInput(
            label="Choose a number (0 - 1000)",
            placeholder="Enter your number...",
            required=True,
            max_length=4
        )

        self.add_item(self.number_input)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        if self.guild_id not in self.game_cog.active_games:

            return await interaction.response.send_message(
                "❌ This game already ended.",
                ephemeral=True
            )

        game = self.game_cog.active_games[self.guild_id]

        if interaction.user not in game["players"]:

            return await interaction.response.send_message(
                "❌ You are not part of this game.",
                ephemeral=True
            )

        try:

            number = int(self.number_input.value)

        except ValueError:

            return await interaction.response.send_message(
                "❌ Enter a valid number.",
                ephemeral=True
            )

        # LIMIT
        if number < 0 or number > 1000:

            return await interaction.response.send_message(
                "❌ Number must be between 0 and 1000.",
                ephemeral=True
            )

        # ALREADY SUBMITTED
        if interaction.user.id in game["numbers"]:

            return await interaction.response.send_message(
                "❌ You already locked your number.",
                ephemeral=True
            )

        game["numbers"][interaction.user.id] = number

        await interaction.response.send_message(
            f"🔒 Locked in: **{number}**",
            ephemeral=True
        )

        await self.game_cog.update_submission_board(
            self.guild_id
        )


# ─────────────────────────
# GAME CONTROL VIEW
# ─────────────────────────

class GameControlView(discord.ui.View):

    def __init__(self, game_cog, guild_id):

        super().__init__(timeout=None)

        self.game_cog = game_cog
        self.guild_id = guild_id

    @discord.ui.button(
        label="Submit Number",
        style=discord.ButtonStyle.primary,
        emoji="🎲"
    )
    async def submit_number(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        modal = PickNumberModal(
            self.game_cog,
            self.guild_id
        )

        await interaction.response.send_modal(
            modal
        )


# ─────────────────────────
# LOBBY VIEW
# ─────────────────────────

class LobbyView(discord.ui.View):

    def __init__(self):

        super().__init__(timeout=20)

        self.players = []

    @discord.ui.button(
        label="Join Arena",
        style=discord.ButtonStyle.success,
        emoji="🎮"
    )
    async def join_game(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user in self.players:

            return await interaction.response.send_message(
                "You already joined.",
                ephemeral=True
            )

        self.players.append(
            interaction.user
        )

        await interaction.response.send_message(
            "⚔️ You joined the match.",
            ephemeral=True
        )


# ─────────────────────────
# MAIN GAME COG
# ─────────────────────────

class AverageGame(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.active_games = average_games

    # ─────────────────────────
    # START GAME
    # ─────────────────────────

    @commands.command(name="average")
    async def average(self, ctx):

        guild = ctx.guild

        if not guild:
            return

        if guild.id in self.active_games:

            return await ctx.send(
                "❌ An Average game is already running."
            )

        embed = discord.Embed(
            title="🎯 Average Arena",
            description=(
                "Press the button below to join.\n\n"
                "🏆 Closest to the final target wins."
            ),
            color=0x5865F2
        )

        embed.add_field(
            name="📌 Rules",
            value=(
                "• Choose a number between `0 - 1000`\n"
                "• Random multiplier every round\n"
                "• Duplicate numbers are disqualified\n"
                "• Inputs stay hidden until reveal"
            ),
            inline=False
        )

        embed.set_footer(
            text="Lobby closes in 20 seconds"
        )

        lobby_view = LobbyView()

        lobby_message = await ctx.send(
            embed=embed,
            view=lobby_view
        )

        await lobby_view.wait()

        players = list(
            dict.fromkeys(
                lobby_view.players
            )
        )

        if len(players) < 2:

            try:
                await lobby_message.edit(
                    view=None
                )
            except:
                pass

            return await ctx.send(
                "❌ Need at least 2 players."
            )

        game = {
            "players": players,
            "numbers": {},
            "channel": ctx.channel,
            "board_msg": None
        }

        self.active_games[guild.id] = game

        player_status = "\n".join([
            f"⏳ {p.mention} — Thinking..."
            for p in players
        ])

        start_embed = discord.Embed(
            title="🏁 Match Started",
            description=(
                "Submit your number below."
            ),
            color=0x57F287
        )

        start_embed.add_field(
            name="📋 Players",
            value=player_status,
            inline=False
        )

        control_view = GameControlView(
            self,
            guild.id
        )

        board_msg = await ctx.send(
            embed=start_embed,
            view=control_view
        )

        game["board_msg"] = board_msg

    # ─────────────────────────
    # UPDATE BOARD
    # ─────────────────────────

    async def update_submission_board(
        self,
        guild_id
    ):

        game = self.active_games.get(
            guild_id
        )

        if not game:
            return

        players = game["players"]
        numbers = game["numbers"]

        status_lines = []

        for player in players:

            if player.id in numbers:

                status_lines.append(
                    f"✅ {player.mention} — Locked"
                )

            else:

                status_lines.append(
                    f"⏳ {player.mention} — Thinking..."
                )

        embed = discord.Embed(
            title="🎲 Match Active",
            description="Waiting for players...",
            color=0xFAA61A
        )

        embed.add_field(
            name="📋 Status",
            value="\n".join(status_lines),
            inline=False
        )

        try:

            await game["board_msg"].edit(
                embed=embed
            )

        except:
            pass

        # EVERYONE SUBMITTED
        if len(numbers) == len(players):

            await asyncio.sleep(1.5)

            await self.finish_game(
                guild_id
            )

    # ─────────────────────────
    # FINISH GAME
    # ─────────────────────────

    async def finish_game(
        self,
        guild_id
    ):

        game = self.active_games.get(
            guild_id
        )

        if not game:
            return

        players = game["players"]
        numbers = game["numbers"]

        board_msg = game["board_msg"]

        try:

            await board_msg.edit(
                view=None
            )

        except:
            pass

        values = list(numbers.values())

        average = sum(values) / len(values)

        # RANDOM MULTIPLIER
        multiplier = random.choice([
            0,
            0.5,
            1,
            1.5,
            2
        ])

        target = average * multiplier

        # ─────────────────────────
        # DUPLICATE PENALTY
        # ─────────────────────────

        number_counts = {}

        for num in values:

            number_counts[num] = (
                number_counts.get(num, 0) + 1
            )

        valid_players = []

        for player in players:

            player_number = numbers[player.id]

            if number_counts[player_number] == 1:

                valid_players.append(
                    player
                )

        # REVEAL TEXT
        reveal = ""

        for player in players:

            num = numbers[player.id]

            if number_counts[num] > 1:

                reveal += (
                    f"• {player.mention}\n"
                    f"## **{num}** ❌ Duplicate\n\n"
                )

            else:

                reveal += (
                    f"• {player.mention}\n"
                    f"## **{num}**\n\n"
                )

        results_embed = discord.Embed(
            title="📊 Results",
            color=0xEB459E
        )

        results_embed.add_field(
            name="🎲 Revealed Numbers",
            value=reveal,
            inline=False
        )

        results_embed.add_field(
            name="🧮 Calculations",
            value=(
                f"📊 Average\n"
                f"## **{average:.2f}**\n\n"

                f"🎲 Multiplier\n"
                f"## **×{multiplier}**\n\n"

                f"🎯 Final Target\n"
                f"## **{target:.2f}**"
            ),
            inline=False
        )

        # EVERYONE DUPLICATED
        if not valid_players:

            results_embed.add_field(
                name="💀 Nobody Won",
                value=(
                    "Everyone copied numbers.\n"
                    "No valid winner."
                ),
                inline=False
            )

            await game["channel"].send(
                embed=results_embed
            )

            del self.active_games[guild_id]

            return

        # DISTANCES
        distances = {

            player.id: abs(
                numbers[player.id] - target
            )

            for player in valid_players
        }

        closest = min(
            distances.values()
        )

        winners = [

            player

            for player in valid_players

            if distances[player.id] == closest
        ]

        # DRAW
        if len(winners) > 1:

            draw_mentions = " ".join([
                p.mention
                for p in winners
            ])

            results_embed.add_field(
                name="🤝 Draw",
                value=(
                    f"{draw_mentions}\n"
                    f"Equal distance to target."
                ),
                inline=False
            )

        # SINGLE WINNER
        else:

            winner = winners[0]

            results_embed.add_field(
                name="🏆 Winner",
                value=(
                    f"{winner.mention}\n\n"
                    f"🎯 Closest To\n"
                    f"## **{target:.2f}**"
                ),
                inline=False
            )

        results_embed.set_footer(
            text="Average Arena"
        )

        await game["channel"].send(
            embed=results_embed
        )

        del self.active_games[guild_id]


# ─────────────────────────
# LOAD COG
# ─────────────────────────

async def setup(bot):

    await bot.add_cog(
        AverageGame(bot)
    )
