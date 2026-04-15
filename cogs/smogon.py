import discord
from discord.ext import commands
from discord.ui import View
import aiohttp
import re

# ─────────────────────────
# NORMALIZATION
# ─────────────────────────

def normalize(name):
    return name.lower().replace(" ", "-").strip()

def fix_pokemon(name):
    name = normalize(name)
    if "mega" in name:
        return name.replace("-mega", "").replace("mega", ""), name
    return name, name

# ─────────────────────────
# FETCH SMOGON HTML
# ─────────────────────────

async def fetch_smogon(pokemon, gen):
    url = f"https://www.smogon.com/dex/{gen}/pokemon/{pokemon}/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status != 200:
                return None
            return await r.text()

# ─────────────────────────
# EXTRACT ONLY OU SETS
# ─────────────────────────

def extract_ou_sets(html):
    if not html:
        return ["No sets found."]

    sections = re.findall(r"<h2.*?>(.*?)</h2>(.*?)</section>", html, re.S)

    results = []

    for title, content in sections:
        if "OU" not in title and "National Dex" not in title:
            continue

        clean = re.sub("<.*?>", "", content)
        clean = re.sub("\n+", "\n", clean)

        results.append(f"**{title.strip()}**\n{clean.strip()[:500]}")

    return results[:3] if results else ["No OU sets found."]

# ─────────────────────────
# BUTTON VIEW
# ─────────────────────────

class SmogonView(View):
    def __init__(self, pokemon):
        super().__init__(timeout=60)
        self.pokemon = pokemon

    async def send_sets(self, interaction, gen, label):
        html = await fetch_smogon(self.pokemon, gen)
        sets = extract_ou_sets(html)

        embed = discord.Embed(
            title=f"{self.pokemon.title()} - {label} OU Sets",
            color=0x00ffcc
        )

        embed.description = "\n\n".join(sets)

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
        poke, gif = fix_pokemon(name)
        api = normalize(name)

        # ───── POKEMON ─────
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://pokeapi.co/api/v2/pokemon/{poke}") as r:
                if r.status == 200:
                    data = await r.json()

                    gif_url = f"https://play.pokemonshowdown.com/sprites/xyani/{gif}.gif"

                    types = [t["type"]["name"].title() for t in data["types"]]
                    abilities = [a["ability"]["name"].title() for a in data["abilities"]]

                    stats = "\n".join(
                        f"{s['stat']['name'].upper()}: {s['base_stat']}"
                        for s in data["stats"]
                    )

                    embed = discord.Embed(title=name.title(), color=0x3498db)
                    embed.set_image(url=gif_url)
                    embed.add_field(name="Type", value=", ".join(types))
                    embed.add_field(name="Abilities", value=", ".join(abilities))
                    embed.add_field(name="Stats", value=stats, inline=False)

                    await ctx.send(embed=embed, view=SmogonView(poke))
                    return

        # ───── MOVE ─────
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://pokeapi.co/api/v2/move/{api}") as r:
                if r.status == 200:
                    data = await r.json()

                    effect_entry = next(
                        (e for e in data["effect_entries"] if e["language"]["name"] == "en"),
                        None
                    )

                    if effect_entry:
                        desc = effect_entry["effect"]

                        if "$effect_chance" in desc:
                            chance = data.get("effect_chance", "")
                            desc = desc.replace("$effect_chance", str(chance))

                        desc = desc.replace("\n", " ").replace("  ", " ")
                    else:
                        desc = "No description"

                    embed = discord.Embed(title=name.title(), color=0xf1c40f)
                    embed.add_field(name="Type", value=data["type"]["name"].title())
                    embed.add_field(name="Power", value=data["power"])
                    embed.add_field(name="Accuracy", value=data["accuracy"])
                    embed.add_field(name="PP", value=data["pp"])
                    embed.add_field(name="Description", value=desc, inline=False)

                    await ctx.send(embed=embed)
                    return

        # ───── ITEM ─────
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://pokeapi.co/api/v2/item/{api}") as r:
                if r.status == 200:
                    data = await r.json()

                    desc = next(
                        (e["effect"] for e in data["effect_entries"] if e["language"]["name"] == "en"),
                        "No description"
                    )

                    embed = discord.Embed(title=name.title(), color=0x2ecc71)
                    embed.set_thumbnail(url=data["sprites"]["default"])
                    embed.add_field(name="Description", value=desc, inline=False)

                    await ctx.send(embed=embed)
                    return

        # ───── ABILITY ─────
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://pokeapi.co/api/v2/ability/{api}") as r:
                if r.status == 200:
                    data = await r.json()

                    desc = next(
                        (e["effect"] for e in data["effect_entries"] if e["language"]["name"] == "en"),
                        "No description"
                    )

                    embed = discord.Embed(title=name.title(), color=0x9b59b6)
                    embed.add_field(name="Ability Effect", value=desc, inline=False)

                    await ctx.send(embed=embed)
                    return

        await ctx.send("❌ Not found.")

# ─────────────────────────
async def setup(bot):
    await bot.add_cog(Smogon(bot))
