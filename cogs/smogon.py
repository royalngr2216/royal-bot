import discord
from discord.ext import commands
from discord.ui import View
import aiohttp
import asyncio
import re
import json

# ─────────────────────────
# CACHE (INSTANT RESPONSES)
# ─────────────────────────
cache = {}

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
# SMOGON FETCH (FAST JSON)
# ─────────────────────────

async def fetch_smogon(pokemon, gen):
    url = f"https://www.smogon.com/dex/{gen}/pokemon/{pokemon}/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status != 200:
                return None
            return await r.text()

def extract_ou_sets(html):
    if not html:
        return ["No sets found."]

    match = re.search(r"window\.__dexSettings = ({.*?});", html)
    if not match:
        return ["No sets found."]

    data = json.loads(match.group(1))
    strategies = data.get("strategies", [])

    results = []

    for strat in strategies:
        format_name = strat.get("format", "")

        if "OU" not in format_name and "National Dex" not in format_name:
            continue

        name = strat.get("name", "Set")
        moves = strat.get("moves", [])
        item = strat.get("items", [""])[0]
        ability = strat.get("abilities", [""])[0]
        evs = strat.get("evconfigs", [""])[0]

        move_text = "\n".join(f"• {m}" for m in moves[:4])

        text = (
            f"**{name} ({format_name})**\n"
            f"Item: {item}\n"
            f"Ability: {ability}\n"
            f"EVs: {evs}\n"
            f"{move_text}"
        )

        results.append(text)

    return results[:2] if results else ["No OU sets found."]

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

        # ⚡ instant response
        msg = await ctx.send("⏳ Searching...")

        # ⚡ cache check
        if name.lower() in cache:
            return await msg.edit(embed=cache[name.lower()])

        poke, gif = fix_pokemon(name)
        api = normalize(name)

        async with aiohttp.ClientSession() as session:

            # ⚡ PARALLEL REQUESTS
            pokemon_task = session.get(f"https://pokeapi.co/api/v2/pokemon/{poke}")
            move_task = session.get(f"https://pokeapi.co/api/v2/move/{api}")
            item_task = session.get(f"https://pokeapi.co/api/v2/item/{api}")
            ability_task = session.get(f"https://pokeapi.co/api/v2/ability/{api}")

            p_res, m_res, i_res, a_res = await asyncio.gather(
                pokemon_task, move_task, item_task, ability_task
            )

            # ───── POKEMON ─────
            if p_res.status == 200:
                data = await p_res.json()

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

                cache[name.lower()] = embed
                return await msg.edit(embed=embed, view=SmogonView(poke))

            # ───── MOVE ─────
            if m_res.status == 200:
                data = await m_res.json()

                effect_entry = next(
                    (e for e in data["effect_entries"] if e["language"]["name"] == "en"),
                    None
                )

                desc = effect_entry["effect"] if effect_entry else "No description"

                if "$effect_chance" in desc:
                    desc = desc.replace("$effect_chance", str(data.get("effect_chance", "")))

                desc = desc.replace("\n", " ").replace("  ", " ")

                embed = discord.Embed(title=name.title(), color=0xf1c40f)
                embed.add_field(name="Type", value=data["type"]["name"].title())
                embed.add_field(name="Power", value=data["power"])
                embed.add_field(name="Accuracy", value=data["accuracy"])
                embed.add_field(name="PP", value=data["pp"])
                embed.add_field(name="Description", value=desc, inline=False)

                cache[name.lower()] = embed
                return await msg.edit(embed=embed)

            # ───── ITEM ─────
            if i_res.status == 200:
                data = await i_res.json()

                desc = next(
                    (e["effect"] for e in data["effect_entries"] if e["language"]["name"] == "en"),
                    "No description"
                )

                embed = discord.Embed(title=name.title(), color=0x2ecc71)
                embed.set_thumbnail(url=data["sprites"]["default"])
                embed.add_field(name="Description", value=desc, inline=False)

                cache[name.lower()] = embed
                return await msg.edit(embed=embed)

            # ───── ABILITY ─────
            if a_res.status == 200:
                data = await a_res.json()

                desc = next(
                    (e["effect"] for e in data["effect_entries"] if e["language"]["name"] == "en"),
                    "No description"
                )

                embed = discord.Embed(title=name.title(), color=0x9b59b6)
                embed.add_field(name="Ability Effect", value=desc, inline=False)

                cache[name.lower()] = embed
                return await msg.edit(embed=embed)

        await msg.edit(content="❌ Not found.")

# ─────────────────────────
async def setup(bot):
    await bot.add_cog(Smogon(bot))
