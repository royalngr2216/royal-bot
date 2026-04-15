import discord
from discord.ext import commands
from discord.ui import View
import aiohttp
import asyncio

# ─────────────────────────
# CACHE
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
# BUTTON VIEW (LINKS ONLY)
# ─────────────────────────

class SmogonView(View):
    def __init__(self, pokemon):
        super().__init__(timeout=60)
        self.pokemon = pokemon

    async def send_link(self, interaction, gen, label):
        url = f"https://www.smogon.com/dex/{gen}/pokemon/{self.pokemon}/"

        embed = discord.Embed(
            title=f"{self.pokemon.title()} - {label}",
            description=f"[Click here for Smogon sets]({url})",
            color=0x00ffcc
        )

        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="ORAS", style=discord.ButtonStyle.primary)
    async def oras(self, interaction, button):
        await self.send_link(interaction, "xy", "ORAS")

    @discord.ui.button(label="SM", style=discord.ButtonStyle.success)
    async def sm(self, interaction, button):
        await self.send_link(interaction, "sm", "SM")

    @discord.ui.button(label="SS", style=discord.ButtonStyle.secondary)
    async def ss(self, interaction, button):
        await self.send_link(interaction, "ss", "SS")

    @discord.ui.button(label="NatDex", style=discord.ButtonStyle.danger)
    async def natdex(self, interaction, button):
        await self.send_link(interaction, "sv", "National Dex")

# ─────────────────────────
# MAIN COG
# ─────────────────────────

class Smogon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def smogon(self, ctx, *, name):

        msg = await ctx.send("⏳ Searching...")

        # CACHE
        if name.lower() in cache:
            return await msg.edit(content="", embed=cache[name.lower()])

        poke, gif = fix_pokemon(name)
        api = normalize(name)

        async with aiohttp.ClientSession() as session:

            # PARALLEL REQUESTS
            p_task = session.get(f"https://pokeapi.co/api/v2/pokemon/{poke}")
            m_task = session.get(f"https://pokeapi.co/api/v2/move/{api}")
            i_task = session.get(f"https://pokeapi.co/api/v2/item/{api}")
            a_task = session.get(f"https://pokeapi.co/api/v2/ability/{api}")

            p_res, m_res, i_res, a_res = await asyncio.gather(
                p_task, m_task, i_task, a_task
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
                return await msg.edit(content="", embed=embed, view=SmogonView(poke))

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
                return await msg.edit(content="", embed=embed)

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
                return await msg.edit(content="", embed=embed)

            # ───── ABILITY (FIXED) ─────
            ability_name = normalize(name)

            # try normal
            async with session.get(f"https://pokeapi.co/api/v2/ability/{ability_name}") as r:
                if r.status == 200:
                    data = await r.json()

                    desc = next(
                        (e["effect"] for e in data["effect_entries"] if e["language"]["name"] == "en"),
                        "No description"
                    )

                    embed = discord.Embed(title=name.title(), color=0x9b59b6)
                    embed.add_field(name="Ability Effect", value=desc, inline=False)

                    cache[name.lower()] = embed
                    return await msg.edit(content="", embed=embed)

            # fallback
            alt = ability_name.replace("-", "")
            async with session.get(f"https://pokeapi.co/api/v2/ability/{alt}") as r2:
                if r2.status == 200:
                    data = await r2.json()

                    desc = next(
                        (e["effect"] for e in data["effect_entries"] if e["language"]["name"] == "en"),
                        "No description"
                    )

                    embed = discord.Embed(title=name.title(), color=0x9b59b6)
                    embed.add_field(name="Ability Effect", value=desc, inline=False)

                    cache[name.lower()] = embed
                    return await msg.edit(content="", embed=embed)

        await msg.edit(content="❌ Not found.")

# ─────────────────────────
async def setup(bot):
    await bot.add_cog(Smogon(bot))
