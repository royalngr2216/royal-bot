import discord
from discord.ext import commands
import random

class DiceGame:
    def __init__(self, p1, p2, target):
        self.p1 = p1
        self.p2 = p2
        self.target = target

        self.turn = p1
        self.scores = {p1.id: [], p2.id: []}
        self.finished = {p1.id: False, p2.id: False}

    def roll(self, user):
        value = random.randint(1, 21)
        self.scores[user.id].append(value)

    def total(self, user):
        return sum(self.scores[user.id])

    def both_done(self):
        return all(self.finished.values())


class DiceView(discord.ui.View):
    def __init__(self, game, ctx, rounds):
        super().__init__(timeout=None)
        self.game = game
        self.ctx = ctx
        self.rounds = rounds
        self.wins = {game.p1.id: 0, game.p2.id: 0}

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.game.turn

    @discord.ui.button(label="🎲 Roll", style=discord.ButtonStyle.green)
    async def roll_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.game.roll(interaction.user)
        await interaction.response.send_message("🎲 Rolled!", ephemeral=True)

    @discord.ui.button(label="➡️ Pass", style=discord.ButtonStyle.blurple)
    async def pass_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.game.finished[interaction.user.id] = True

        # switch turn
        if interaction.user == self.game.p1:
            self.game.turn = self.game.p2
            await interaction.response.send_message(
                f"➡️ {self.game.p2.mention}'s turn!",
                view=self
            )
        else:
            # round ends
            await interaction.response.defer()
            await self.end_round()

    async def end_round(self):
        p1 = self.game.p1
        p2 = self.game.p2

        t = self.game.target
        s1 = self.game.total(p1)
        s2 = self.game.total(p2)

        diff1 = abs(t - s1)
        diff2 = abs(t - s2)

        if diff1 < diff2:
            winner = p1
        elif diff2 < diff1:
            winner = p2
        else:
            winner = None

        result_text = (
            f"🎯 Target: **{t}**\n\n"
            f"{p1.mention} → {s1}\n"
            f"{p2.mention} → {s2}\n\n"
        )

        if winner:
            self.wins[winner.id] += 1
            result_text += f"🏆 {winner.mention} wins the round!"
        else:
            result_text += "🤝 It's a tie!"

        await self.ctx.send(result_text)

        # check match win
        needed = self.rounds // 2 + 1
        if self.wins[p1.id] >= needed or self.wins[p2.id] >= needed:
            final_winner = p1 if self.wins[p1.id] > self.wins[p2.id] else p2
            await self.ctx.send(f"👑 {final_winner.mention} wins the match!")
            self.stop()
            return

        # new round
        new_target = random.randint(1, 21)
        self.game = DiceGame(p1, p2, new_target)

        await self.ctx.send(
            f"🔄 New Round!\n🎯 Target is **{new_target}**\n\n"
            f"{p1.mention}, your turn!",
            view=self
        )


class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dice(self, ctx, opponent: discord.Member, rounds: int):
        if rounds not in [1, 3, 5, 7]:
            await ctx.send("❌ Choose rounds: 1, 3, 5, or 7")
            return

        if opponent.bot:
            await ctx.send("❌ You can't play against a bot.")
            return

        target = random.randint(1, 21)

        game = DiceGame(ctx.author, opponent, target)
        view = DiceView(game, ctx, rounds)

        await ctx.send(
            f"🎲 **Dice Game Started!**\n\n"
            f"🎯 Target Number: **{target}**\n"
            f"{ctx.author.mention} goes first!\n\n"
            f"Choose wisely 👇",
            view=view
        )


async def setup(bot):
    await bot.add_cog(Dice(bot))