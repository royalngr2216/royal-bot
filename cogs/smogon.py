import discord
from discord.ext import commands
from discord.ui import View
import aiohttp

# ─────────────────────────
# NORMALIZATION FUNCTIONS
# ─────────────────────────

def normalize_name(name: str):
    name = name.lower().strip()
    name = name.replace(" ", "-")

    while "--" in name:
        name = name.replace("--", "-")

    return name


def fix_pokemon_name(name: str):
    name = normalize_name(name)

    # Handle mega forms
    if "mega" in name:
        base = name.replace("-mega", "").replace("mega", "")
        return base, name  # (pokeapi_name, gif_name)

    return name, name


def normalize_api_name(name: str):
    name = name.lower().strip()
    name = name.replace(" ", "-")

    # Special fixes (expand later if needed)
    fixes = {
        "will-o-wisp": "will-o-wisp",
        "air-balloon": "air-balloon"
    }

    return fixes.get(name, name)


# ─────────────────────────
# BUTTON VIEW
# ─────────────────────────

class SmogonView(View):
    def __init__(self, pokemon):
        super().__init__(timeout=60)
        self.pokemon = pokemon

    async def send_sets(self, interaction, gen, label):
        url = f"https://www.smogon.com/dex/{gen}/pokemon/{self.pokemon}/"

        embed = discord.Embed(
            title=f"{self.pokemon.title()} - {label}",
            description=f"[Click here for Smogon sets]({url})",
            color=0x00ffcc
        )

        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="ORAS", style=discord.ButtonStyle.primary)
    async def oras(self, interaction, button):
        await self.send_sets(interaction, "xy", "ORAS")

    @discord.ui.button(label="SM", style=discord.ButtonStyle.success)
    async def sm(self, interaction, button):
        await self.send_sets(interaction, "sm", "SM")

    @discord.ui.button(label="SS", style=discord.ButtonStyle.secondary)
    async def ss(self, interaction, button):
        await self.send_sets(interaction, "ss", "SS")

    @discord.ui.button(label="NatDex", style=discord.ButtonStyle.danger)
    async def natdex(self, interaction, button):
        await self.send_sets(interaction, "sv", "National Dex")


# ─────────────────────────
# MAIN COG
# ─────────────────────────

class Smogon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def smogon(self, ctx, *, name):
        pokeapi_name, gif_name = fix_pokemon_name(name)
        api_name = normalize_api_name(name)

        # ───── TRY POKEMON ─────
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://pokeapi.co/api/v2/pokemon/{pokeapi_name}") as r:
                if r.status == 200:
                    data = await r.json()

                    gif = f"https://play.pokemonshowdown.com/sprites/xyani/{gif_name}.gif"

                    types = [t['type']['name'].title() for t in data['types']]
                    abilities = [a['ability']['name'].title() for a in data['abilities']]

                    stats = "\n".join(
                        f"{s['stat']['name'].upper()}: {s['base_stat']}"
                        for s in data['stats']
                    )

                    embed = discord.Embed(
                        title=name.title(),
                        color=0x3498db
                    )
                    embed.set_image(url=gif)
                    embed.add_field(name="Type", value=", ".join(types))
                    embed.add_field(name="Abilities", value=", ".join(abilities))
                    embed.add_field(name="Stats", value=stats, inline=False)

                    await ctx.send(embed=embed, view=SmogonView(pokeapi_name))
                    return

        # ───── TRY MOVE ─────
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://pokeapi.co/api/v2/move/{api_name}") as r:
                if r.status == 200:
                    data = await r.json()

                    embed = discord.Embed(
                        title=name.title(),
                        color=0xf1c40f
                    )
                    embed.add_field(name="Type", value=data["type"]["name"].title())
                    embed.add_field(name="Power", value=data["power"])
                    embed.add_field(name="Accuracy", value=data["accuracy"])
                    embed.add_field(name="PP", value=data["pp"])
                    embed.add_field(
                        name="Description",
                        value=data["effect_entries"][0]["effect"],
                        inline=False
                    )

                    await ctx.send(embed=embed)
                    return

        # ───── TRY ITEM ─────
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://pokeapi.co/api/v2/item/{api_name}") as r:
                if r.status == 200:
                    data = await r.json()

                    embed = discord.Embed(
                        title=name.title(),
                        color=0x2ecc71
                    )
                    embed.set_thumbnail(url=data["sprites"]["default"])
                    embed.add_field(
                        name="Description",
                        value=data["effect_entries"][0]["effect"],
                        inline=False
                    )

                    await ctx.send(embed=embed)
                    return

        await ctx.send("❌ Not found. Try Pokémon, move, or item.")


# ─────────────────────────
# SETUP
# ─────────────────────────

async def setup(bot):
    await bot.add_cog(Smogon(bot))
