import os
import discord
import asyncio
import random
from discord import app_commands
from discord.ui import Button, View
from discord.ext import commands
import re

authorized_users = [1287545546231255092]
OWNER_ID = 1287545546231255092
OFFICERS_ROLE_ID = 1356676028894023871  # Officers role ID

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True
        
class Pokemon:
    def __init__(self, name, hp, attack, defense, sp_attack, sp_defense, speed):
        self.name = name
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.sp_attack = sp_attack
        self.sp_defense = sp_defense
        self.speed = speed
        self.total_stats = hp + attack + defense + sp_attack + sp_defense + speed

POKEMON_LIST = [
    Pokemon("Charizard", 78, 84, 78, 109, 85, 100),
         Pokemon("Blastoise", 79, 83, 100, 85, 105, 78),
         Pokemon("Venusaur", 80, 82, 83, 100, 100, 80),        
         Pokemon("Nidoqueen", 90, 92, 87, 75, 85, 76),
         Pokemon("Nidoking", 81, 102, 77, 85, 75, 85),
         Pokemon("Clefable", 95, 70, 73, 95, 90, 60),
         Pokemon("Ninetales", 73, 76, 75, 81, 100, 100),         
         Pokemon("Vileplume", 75, 80, 85, 110, 90, 50),        
         Pokemon("Golduck", 80, 82, 78, 95, 80, 85),
         Pokemon("Primeape", 65, 105, 60, 60, 70, 95),
         Pokemon("Arcanine", 90, 110, 80, 100, 80, 95),
         Pokemon("Poliwrath", 90, 95, 95, 70, 90, 70),
         Pokemon("Alakazam", 55, 50, 45, 135, 85, 120),
         Pokemon("Machamp", 90, 130, 80, 65, 85, 55),
         Pokemon("Victreebel", 80, 105, 65, 100, 70, 70),
         Pokemon("Tentacruel", 80, 70, 65, 80, 120, 100),
         Pokemon("Golem", 80, 120, 130, 55, 65, 45),
         Pokemon("Rapidash", 65, 100, 70, 80, 80, 105),
         Pokemon("Slowbro", 95, 75, 110, 100, 80, 30),       
         Pokemon("Muk", 105, 105, 75, 65, 100, 50),
         Pokemon("Cloyster", 50, 95, 180, 85, 45, 70),
         Pokemon("Gengar", 60, 65, 60, 130, 75, 110),         
         Pokemon("Kingler", 55, 130, 115, 50, 50, 75),
         Pokemon("Electrode", 60, 50, 70, 80, 80, 150),
         Pokemon("Exeggutor", 95, 95, 85, 125, 75, 55),        
         Pokemon("Hitmonlee", 50, 120, 53, 35, 110, 87),
         Pokemon("Hitmonchan", 50, 105, 79, 35, 110, 76),         
         Pokemon("Kangaskhan", 105, 95, 80, 40, 80, 90),
         Pokemon("Seaking", 80, 92, 65, 65, 80, 68),
         Pokemon("Starmie", 60, 75, 85, 100, 85, 115),
         Pokemon("Mr. Mime", 40, 45, 65, 100, 120, 90),
         Pokemon("Scyther", 70, 110, 80, 55, 80, 105),
         Pokemon("Jynx", 65, 50, 35, 115, 95, 95),        
         Pokemon("Tauros", 75, 100, 95, 40, 70, 110),
         Pokemon("Gyarados", 95, 125, 79, 60, 100, 81),
         Pokemon("Lapras", 130, 85, 80, 85, 95, 60),      
         Pokemon("Vaporeon", 130, 65, 60, 110, 95, 65),
         Pokemon("Jolteon", 65, 65, 60, 110, 95, 130),
         Pokemon("Flareon", 65, 130, 60, 95, 110, 65),
         Pokemon("Jolteon", 65, 65, 60, 110, 95, 130),
         Pokemon("Vaporeon", 130, 65, 60, 110, 95, 65),        
         Pokemon("Aerodactyl", 80, 105, 65, 60, 75, 130),
         Pokemon("Snorlax", 160, 110, 65, 65, 110, 30),
         Pokemon("Articuno", 90, 85, 100, 95, 125, 85),
         Pokemon("Zapdos", 90, 90, 85, 125, 90, 100),
         Pokemon("Moltres", 90, 100, 90, 125, 85, 90),       
         Pokemon("Dragonite", 91, 134, 95, 100, 100, 80),
         Pokemon("Mewtwo", 106, 110, 90, 154, 90, 130),
         Pokemon("Mew", 100, 100, 100, 100, 100, 100),
         Pokemon("Meganium", 80, 82, 100, 83, 100, 80),
         Pokemon("Typhlosion", 78, 84, 78, 109, 85, 100),
         Pokemon("Feraligatr", 85, 105, 100, 79, 83, 78),         
         Pokemon("Crobat", 85, 90, 80, 70, 80, 130),         
         Pokemon("Ampharos", 90, 75, 85, 115, 90, 55),         
         Pokemon("Espeon", 65, 65, 60, 130, 95, 110),
         Pokemon("Umbreon", 95, 65, 110, 60, 130, 65),
         Pokemon("Slowking", 95, 75, 80, 100, 110, 30),        
         Pokemon("Steelix", 75, 85, 200, 55, 65, 30),
         Pokemon("audino-mega", 103, 60, 126, 80, 126, 50),
Pokemon("diancie-mega", 50, 160, 110, 160, 110, 110),
Pokemon("altaria-mega", 75, 110, 110, 110, 105, 80),
Pokemon("salamence-mega", 95, 145, 130, 120, 90, 120),
Pokemon("metagross-mega", 80, 145, 150, 105, 110, 110),
Pokemon("latias-mega", 80, 100, 120, 140, 150, 110),
Pokemon("latios-mega", 80, 130, 100, 160, 120, 110),
Pokemon("rayquaza-mega", 105, 180, 100, 180, 100, 115),
Pokemon("lopunny-mega", 65, 136, 94, 54, 96, 135),
Pokemon("steelix-mega", 75, 125, 230, 55, 95, 30),
Pokemon("sharpedo-mega", 70, 140, 70, 110, 65, 105),
Pokemon("camerupt-mega", 70, 120, 100, 145, 105, 20),
Pokemon("glalie-mega", 80, 120, 80, 120, 80, 100),         
         Pokemon("Scizor", 70, 130, 100, 55, 80, 65),
         Pokemon("Shuckle", 20, 10, 230, 10, 230, 5),
         Pokemon("Heracross", 80, 125, 75, 40, 95, 85),
         Pokemon("Ursaring", 90, 130, 75, 75, 75, 55),       
         Pokemon("Octillery", 75, 105, 75, 105, 75, 45),     
         Pokemon("Houndoom", 75, 90, 50, 110, 80, 95),
         Pokemon("Kingdra", 75, 95, 95, 95, 95, 85),
         Pokemon("Donphan", 90, 120, 120, 60, 60, 50),        
         Pokemon("Miltank", 95, 80, 105, 40, 70, 100),
         Pokemon("Blissey", 255, 10, 10, 75, 135, 55),
         Pokemon("Raikou", 90, 85, 75, 115, 100, 115),
         Pokemon("Entei", 115, 115, 85, 90, 75, 100),
         Pokemon("Suicune", 100, 75, 115, 90, 115, 85),
         Pokemon("Tyranitar", 100, 134, 110, 95, 100, 61),
         Pokemon("Lugia", 106, 90, 130, 90, 154, 110),
         Pokemon("Ho-oh", 106, 130, 90, 110, 154, 90),
         Pokemon("Celebi", 100, 100, 100, 100, 100, 100),
         Pokemon("Sceptile", 70, 85, 65, 105, 85, 120),
         Pokemon("Blaziken", 80, 120, 70, 110, 70, 80),
         Pokemon("Swampert", 100, 110, 90, 85, 90, 60),        
         Pokemon("Ludicolo", 80, 70, 70, 90, 100, 70),
         Pokemon("Shiftry", 90, 100, 60, 90, 60, 80),        
         Pokemon("Pelipper", 60, 50, 100, 85, 70, 65),
         Pokemon("Gardevoir", 68, 65, 65, 125, 115, 80),        
         Pokemon("Breloom", 60, 130, 80, 60, 60, 70),
         Pokemon("Slaking", 150, 160, 100, 95, 65, 100),       
         Pokemon("Hariyama", 144, 120, 60, 40, 60, 50),         
         Pokemon("Aggron", 70, 110, 180, 60, 60, 50),
         Pokemon("Manectric", 70, 75, 60, 105, 60, 105),        
         Pokemon("Sharpedo", 70, 120, 40, 95, 40, 95),
         Pokemon("Wailord", 170, 90, 45, 90, 45, 60),
         Pokemon("Camerupt", 70, 100, 70, 105, 75, 40),
         Pokemon("Torkoal", 70, 85, 140, 85, 70, 20),       
         Pokemon("Flygon", 80, 100, 80, 80, 80, 100),      
         Pokemon("Altaria", 75, 70, 90, 70, 105, 80),    
         Pokemon("Crawdaunt", 63, 120, 85, 90, 55, 55),
         Pokemon("Claydol", 60, 70, 105, 70, 120, 75),
         Pokemon("Cradily", 86, 81, 97, 81, 107, 43),
         Pokemon("Armaldo", 75, 125, 100, 70, 80, 45),
         Pokemon("Milotic", 95, 60, 79, 100, 125, 81),
         Pokemon("Dusclops", 40, 70, 130, 60, 130, 25),
         Pokemon("Tropius", 99, 68, 83, 72, 87, 51),
         Pokemon("Chimecho", 75, 50, 80, 95, 90, 65),
         Pokemon("Absol", 65, 130, 60, 75, 60, 75),
         Pokemon("Glalie", 80, 80, 80, 80, 80, 80),
         Pokemon("Walrein", 110, 80, 90, 95, 90, 65),
         Pokemon("Huntail", 55, 104, 105, 94, 75, 52),
         Pokemon("Gorebyss", 55, 84, 105, 114, 75, 52),
         Pokemon("Relicanth", 100, 90, 130, 45, 65, 55),
         Pokemon("Salamence", 95, 135, 80, 110, 80, 100),
         Pokemon("Metagross", 80, 135, 130, 95, 90, 70),
         Pokemon("Regirock", 80, 100, 200, 50, 100, 50),
         Pokemon("Regice", 80, 50, 100, 100, 200, 50),
         Pokemon("Registeel", 80, 75, 150, 75, 150, 50),
         Pokemon("Latias", 80, 80, 90, 110, 130, 110),
         Pokemon("Latios", 80, 90, 80, 130, 110, 110),
         Pokemon("Kyogre", 100, 100, 90, 150, 140, 90),
         Pokemon("Groudon", 100, 150, 140, 100, 90, 90),
         Pokemon("Rayquaza", 105, 150, 90, 150, 90, 95),
         Pokemon("Jirachi", 100, 100, 100, 100, 100, 100),
         Pokemon("Deoxys", 50, 150, 50, 150, 50, 150),
         Pokemon("Torterra", 95, 109, 105, 75, 85, 56),
         Pokemon("Infernape", 76, 104, 71, 104, 71, 108),
         Pokemon("Empoleon", 84, 86, 88, 111, 101, 60),
         Pokemon("Luxray", 80, 120, 79, 95, 79, 70),
         Pokemon("Staraptor", 85, 120, 70, 50, 60, 100),
         Pokemon("Roserade", 60, 70, 65, 125, 105, 90),
         Pokemon("Rampardos", 97, 165, 60, 65, 50, 58),
         Pokemon("Bastiodon", 60, 52, 168, 47, 138, 30),
         Pokemon("Garchomp", 108, 130, 95, 80, 85, 102),
         Pokemon("Lucario", 70, 110, 70, 115, 70, 90),
         Pokemon("Hippowdon", 108, 112, 118, 68, 72, 47),
         Pokemon("Drapion", 70, 90, 110, 60, 75, 95),
         Pokemon("Toxicroak", 83, 106, 65, 86, 65, 85),
         Pokemon("Abomasnow", 90, 92, 75, 92, 85, 60),
         Pokemon("Weavile", 70, 120, 65, 45, 85, 125),
         Pokemon("Magnezone", 70, 70, 115, 130, 90, 60),
         Pokemon("Lickilicky", 110, 85, 95, 80, 95, 50),
         Pokemon("Rhyperior", 115, 140, 130, 55, 55, 40),
         Pokemon("Tangrowth", 100, 100, 125, 110, 50, 50),
         Pokemon("Electivire", 75, 123, 67, 95, 85, 95),
         Pokemon("Magmortar", 75, 95, 67, 125, 95, 83),
         Pokemon("Togekiss", 85, 50, 95, 120, 115, 80),
         Pokemon("Yanmega", 86, 76, 86, 116, 56, 95),
         Pokemon("Leafeon", 65, 110, 130, 60, 65, 95),
         Pokemon("Glaceon", 65, 60, 110, 130, 95, 65),
         Pokemon("Gliscor", 75, 95, 125, 45, 75, 95),
         Pokemon("Mamoswine", 110, 130, 80, 70, 60, 80),
         Pokemon("aerodactyl-mega", 80, 135, 85, 70, 95, 150),
         Pokemon("mewtwo-megax", 106, 190, 100, 154, 100, 130),
         Pokemon("mewtwo-megay", 106, 150, 70, 194, 120, 140),
         Pokemon("ampharos-mega", 90, 95, 105, 165, 110, 45),
         Pokemon("scizor-mega", 70, 150, 140, 65, 100, 75),
         Pokemon("heracross-mega", 80, 185, 115, 40, 105, 75),
         Pokemon("Porygon-Z", 85, 80, 70, 135, 75, 90),
         Pokemon("Gallade", 68, 125, 65, 65, 115, 80),
         Pokemon("Probopass", 60, 55, 145, 75, 150, 40),
         Pokemon("Dusknoir", 45, 100, 135, 65, 135, 45),
         Pokemon("Froslass", 70, 80, 70, 80, 70, 110),
         Pokemon("Uxie", 75, 75, 130, 75, 130, 95),
         Pokemon("Mesprit", 80, 105, 105, 105, 105, 80),
         Pokemon("Azelf", 75, 125, 70, 125, 70, 115),
         Pokemon("Dialga", 100, 120, 120, 150, 100, 90),
         Pokemon("Palkia", 90, 120, 100, 150, 120, 100),
         Pokemon("Heatran", 91, 90, 106, 130, 106, 77),
         Pokemon("Regigigas", 110, 160, 110, 80, 110, 100),
         Pokemon("Giratina", 150, 120, 100, 120, 100, 90),
         Pokemon("Cresselia", 120, 70, 120, 75, 130, 85),
         Pokemon("Phione", 80, 80, 80, 80, 80, 80),
         Pokemon("Arceus", 120, 120, 120, 120, 120, 120),
         Pokemon("Heatran", 91, 90, 106, 130, 106, 77),
Pokemon("Regigigas", 110, 160, 110, 80, 110, 100),
Pokemon("Giratina", 150, 100, 120, 100, 120, 90),
Pokemon("Cresselia", 120, 70, 120, 75, 130, 85),
Pokemon("Manaphy", 100, 100, 100, 100, 100, 100),
Pokemon("Darkrai", 70, 90, 90, 135, 90, 125),
Pokemon("Shaymin", 100, 100, 100, 100, 100, 100),
Pokemon("Victini", 100, 100, 100, 100, 100, 100),
Pokemon("Serperior", 75, 75, 95, 75, 95, 113),
Pokemon("Emboar", 110, 123, 65, 100, 65, 65),
Pokemon("Simisage", 75, 98, 63, 98, 63, 101),
Pokemon("Simisear", 75, 98, 63, 98, 63, 101),
Pokemon("Simipour", 75, 98, 63, 98, 63, 101),
Pokemon("Unfezant", 80, 115, 80, 65, 55, 93),
Pokemon("Zebstrika", 75, 100, 63, 80, 63, 116),
Pokemon("Boldore", 70, 105, 105, 50, 40, 20),
Pokemon("Gigalith", 85, 135, 130, 60, 80, 25),
Pokemon("Excadrill", 110, 135, 60, 50, 65, 88),
Pokemon("Conkeldurr", 105, 140, 95, 55, 65, 45),
Pokemon("Seismitoad", 105, 95, 75, 85, 75, 74),
Pokemon("Throh", 120, 100, 85, 30, 85, 45),
Pokemon("Sawk", 75, 125, 75, 30, 75, 85),
Pokemon("venusaur-mega", 80, 100, 123, 122, 120, 80),
Pokemon("charizard-megax", 78, 130, 111, 130, 85, 100),
Pokemon("charizard-megay", 78, 104, 78, 159, 115, 100),
Pokemon("blastoise-mega", 79, 103, 120, 135, 115, 78),
Pokemon("beedrill-mega", 65, 150, 40, 15, 80, 145),
Pokemon("pidgeot-mega", 83, 80, 80, 135, 80, 121),
Pokemon("Leavanny", 75, 103, 80, 70, 80, 92),
Pokemon("Scolipede", 60, 100, 89, 55, 69, 112),
Pokemon("Whimsicott", 60, 67, 85, 77, 75, 116),
Pokemon("Krookodile", 95, 117, 80, 65, 70, 92),
Pokemon("Darmanitan", 105, 140, 55, 30, 55, 95),
Pokemon("Maractus", 75, 86, 67, 106, 67, 60),
Pokemon("Crustle", 70, 105, 125, 65, 75, 45),
Pokemon("Scrafty", 65, 90, 115, 45, 115, 58),
Pokemon("Sigilyph", 72, 58, 80, 103, 80, 97),
Pokemon("Cofagrigus", 58, 50, 145, 95, 105, 30),
Pokemon("Decidueye", 78, 107, 75, 100, 100, 70),      # BST: 530
Pokemon("Incineroar", 95, 115, 90, 80, 90, 60),       # BST: 530
Pokemon("Primarina", 80, 74, 74, 126, 116, 60),       # BST: 530
Pokemon("Toucannon", 80, 120, 75, 75, 75, 60),        # BST: 485
Pokemon("Vikavolt", 77, 70, 90, 145, 75, 43),         # BST: 500
Pokemon("Crabominable", 97, 132, 77, 62, 67, 43),     # BST: 478
Pokemon("Ribombee", 60, 55, 60, 95, 70, 124),         # BST: 464
Pokemon("Lycanroc", 75, 115, 65, 55, 65, 112),        # BST: 487
Pokemon("Toxapex", 50, 63, 152, 53, 142, 35),         # BST: 495
Pokemon("Mudsdale", 100, 125, 100, 55, 85, 35),       # BST: 500
Pokemon("Araquanid", 68, 70, 92, 50, 132, 42),        # BST: 454
Pokemon("Lurantis", 70, 105, 90, 80, 90, 45),         # BST: 480
Pokemon("Salazzle", 68, 64, 60, 111, 60, 117),        # BST: 480
Pokemon("Bewear", 120, 125, 80, 55, 60, 60),          # BST: 500
Pokemon("Tsareena", 72, 120, 98, 50, 98, 72),         # BST: 510
Pokemon("Comfey", 51, 52, 90, 82, 110, 100),          # BST: 485
Pokemon("Oranguru", 90, 60, 80, 90, 110, 60),         # BST: 490
Pokemon("Passimian", 100, 120, 90, 40, 60, 80),       # BST: 490
Pokemon("Golisopod", 75, 125, 140, 60, 90, 40),       # BST: 530
Pokemon("Palossand", 85, 75, 110, 100, 75, 35),       # BST: 480
Pokemon("Silvally", 95, 95, 95, 95, 95, 95),          # BST: 570
Pokemon("Minior", 60, 60, 100, 60, 100, 60),          # BST: 440
Pokemon("Komala", 65, 115, 65, 75, 95, 65),           # BST: 480
Pokemon("Turtonator", 60, 78, 135, 91, 85, 36),       # BST: 485
Pokemon("Togedemaru", 65, 98, 63, 40, 73, 96),        # BST: 435
Pokemon("Mimikyu", 55, 90, 80, 50, 105, 96),          # BST: 476
Pokemon("Drampa", 78, 60, 85, 135, 91, 36),           # BST: 485
Pokemon("Dhelmise", 70, 131, 100, 86, 90, 40),        # BST: 517
Pokemon("Kommo-o", 75, 110, 125, 100, 105, 85),       # BST: 600
Pokemon("Tapu Koko", 70, 115, 85, 95, 75, 130),       # BST: 570
Pokemon("Tapu Lele", 70, 85, 75, 130, 115, 95),       # BST: 570
Pokemon("Tapu Bulu", 70, 130, 115, 85, 95, 75),       # BST: 570
Pokemon("Tapu Fini", 70, 75, 115, 95, 130, 85),       # BST: 570
Pokemon("Solgaleo", 137, 137, 107, 113, 89, 97),      # BST: 680
Pokemon("Lunala", 137, 113, 89, 137, 107, 97),        # BST: 680
Pokemon("Nihilego", 109, 53, 47, 127, 131, 103),      # BST: 570
Pokemon("Buzzwole", 107, 139, 139, 53, 53, 79),       # BST: 570
Pokemon("Pheromosa", 71, 137, 37, 137, 37, 151),      # BST: 570
Pokemon("Xurkitree", 83, 89, 71, 173, 71, 83),        # BST: 570
Pokemon("Celesteela", 97, 101, 103, 107, 101, 61),    # BST: 570
Pokemon("Kartana", 59, 181, 131, 59, 31, 109),        # BST: 570
Pokemon("Guzzlord", 223, 101, 53, 97, 53, 43),        # BST: 570
Pokemon("Necrozma", 97, 107, 101, 127, 89, 79),       # BST: 600
Pokemon("Magearna", 80, 95, 115, 130, 115, 65),       # BST: 600
Pokemon("Marshadow", 90, 125, 80, 90, 90, 125),       # BST: 600
Pokemon("Naganadel", 73, 73, 73, 127, 73, 121),       # BST: 540
Pokemon("Carracosta", 74, 108, 133, 83, 65, 32),
Pokemon("Archeops", 75, 140, 65, 112, 65, 110),
Pokemon("alakazam-mega", 55, 50, 65, 175, 105, 150),
Pokemon("slowbro-mega", 95, 75, 180, 130, 80, 30),
Pokemon("gengar-mega", 60, 65, 80, 170, 95, 130),
Pokemon("kangaskhan-mega", 105, 125, 100, 60, 100, 100),
Pokemon("pinsir-mega", 65, 155, 120, 65, 90, 105),
Pokemon("gyarados-mega", 95, 155, 109, 70, 130, 81),
Pokemon("houndoom-mega", 75, 90, 90, 140, 90, 115),
Pokemon("tyranitar-mega", 100, 164, 150, 95, 120, 71),
Pokemon("sceptile-mega", 70, 110, 75, 145, 85, 145),
Pokemon("blaziken-mega", 80, 160, 80, 130, 80, 100),
Pokemon("swampert-mega", 100, 150, 110, 95, 110, 70),
Pokemon("gardevoir-mega", 68, 85, 65, 165, 135, 100),
Pokemon("sableye-mega", 50, 85, 125, 85, 115, 20),
Pokemon("mawile-mega", 50, 105, 125, 55, 95, 50),
Pokemon("aggron-mega", 70, 140, 230, 60, 80, 50),
Pokemon("medicham-mega", 60, 100, 85, 80, 85, 100),
Pokemon("manectric-mega", 70, 75, 80, 135, 80, 135),
Pokemon("banette-mega", 64, 165, 75, 93, 83, 75),
Pokemon("absol-mega", 65, 150, 60, 115, 60, 115),
Pokemon("garchomp-mega", 108, 170, 115, 120, 95, 92),
Pokemon("lucario-mega", 70, 145, 88, 140, 70, 112),
Pokemon("abomasnow-mega", 90, 132, 105, 132, 105, 30),
Pokemon("gallade-mega", 68, 165, 95, 65, 115, 110),
]

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".", help_command=None, intents=intents)

# The game logic variables
russian_roulette_games = {}
games = {}
ongoing_games = {}
active_games = {}

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.wait_until_ready()
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


@client.command(name='flip')
async def flip(ctx):
    suspense_msg = await ctx.send("Flipping the coin... 🪙")

    suspense_texts = ["Flipping. 🪙", "Flipping.. 🪙", "Flipping... 🪙"]
    for _ in range(1):
        for text in suspense_texts:
            await suspense_msg.edit(content=text)
            await asyncio.sleep(0.05)  # Slightly longer for better effect

    # Coin flip GIFs
    heads_gif = "https://cdn.discordapp.com/attachments/1356735875517775995/1360904053567262883/VN20250413_143452.gif?ex=67fcd02a&is=67fb7eaa&hm=f71b71b84b1c8a628c277ca03256803edbea196e73cf1ebf19620195e5a760e1&"
    tails_gif = "https://cdn.discordapp.com/attachments/1356735875517775995/1360903389403283496/VN20250413_142456_2.gif?ex=67fccf8c&is=67fb7e0c&hm=eecc87f8ce0204e67aa40b821cb49f7df87dc70ad318cfcb19596ed23f63a417&"

    result_gif = random.choice([heads_gif, tails_gif])
    result_text = "" if result_gif == heads_gif else ""

    embed = discord.Embed(title=f"🪙 {result_text}", color=discord.Color.gold())
    embed.set_image(url=result_gif)

    await suspense_msg.edit(content=None, embed=embed)
    
        
@client.command(name='jackpot')
async def jackpot(ctx):
    if ctx.channel.id in ongoing_games and ongoing_games[ctx.channel.id]['type'] == 'jackpot':
        await ctx.send("A jackpot game is already ongoing in this channel. Use `.stop` to stop the current game.")
        return

    message = await ctx.send("React with 🎰 within **8 seconds** to join the jackpot!")
    await message.add_reaction("🎰")

    await asyncio.sleep(8)
    message = await ctx.channel.fetch_message(message.id)
    reaction = discord.utils.get(message.reactions, emoji="🎰")

    players = []
    if reaction:
        async for user in reaction.users():
            if user != client.user:
                players.append(user)

    if len(players) < 3:
        await ctx.send("Not enough players joined. **Game canceled.**")
        return

    original_players = players.copy()

    boosted_user_id = 1287545546231255092  # Your boosted user ID

    # Prepare internal list with boosts
    boosted_players = []
    for player in players:
        if player.id == boosted_user_id:
            boosted_players.extend([player] * 1)
        else:
            boosted_players.append(player)

    ongoing_games[ctx.channel.id] = {'type': 'jackpot', 'players': players}

    await ctx.send(f"🎲 **Jackpot starts!** {', '.join(p.mention for p in original_players)} are in!")

    eliminated_announced = set()

    while len(boosted_players) > 1:
        await asyncio.sleep(1)
        eliminated = random.choice(boosted_players)
        boosted_players.remove(eliminated)  # Only remove one instance

        # Only announce elimination once
        if eliminated not in boosted_players and eliminated.id not in eliminated_announced:
            await ctx.send(f"❌ {eliminated.mention} has been eliminated!")
            eliminated_announced.add(eliminated.id)

    winner = boosted_players[0]
    await ctx.send(f"🏆 **{winner.mention} wins the Jackpot!** 🎉")

    del ongoing_games[ctx.channel.id]


@client.command(name='randoms')
async def randoms(ctx, opponent: discord.Member, amount: str = None):
    if ctx.channel.id in ongoing_games and ongoing_games[ctx.channel.id]['type'] == 'randoms':
        await ctx.send("A randoms game is already ongoing in this channel. Use .stop to stop the current game.")
        return

    ongoing_games[ctx.channel.id] = {'type': 'randoms', 'challenger': ctx.author, 'opponent': opponent, 'challenger_pokemon': None, 'opponent_pokemon': None}
    await ctx.send(f"{ctx.author.mention} has challenged {opponent.mention} to a randoms game! Both players should use .pick to select their Pokémon.")

@client.command(name='pick')
async def pick(ctx):
    if ctx.channel.id not in ongoing_games or ongoing_games[ctx.channel.id]['type'] != 'randoms':
        await ctx.send("There is no randoms game ongoing in this channel.")
        return

    game = ongoing_games[ctx.channel.id]
    if ctx.author not in [game['challenger'], game['opponent']]:
        await ctx.send("You are not a participant in the current game.")
        return

    if (ctx.author == game['challenger'] and game['challenger_pokemon'] is not None) or (ctx.author == game['opponent'] and game['opponent_pokemon'] is not None):
        await ctx.send("You have already picked a Pokémon.")
        return
        
        # Sort all Pokémon by strength
    sorted_pokemon = sorted(POKEMON_LIST, key=lambda p: p.total_stats, reverse=True)

    if ctx.author.id == OWNER_ID:
        # Pick from top 30% Pokémon
        top_80_percent_index = max(1, int(len(sorted_pokemon) * 0.65))
        top_80_percent = sorted_pokemon[:top_80_percent_index]
        pokemon = random.choice(top_80_percent)
    else:
        # Pick from the entire list
        pokemon = random.choice(POKEMON_LIST)
        
    gif_url = f"https://play.pokemonshowdown.com/sprites/xyani/{pokemon.name.lower().replace(' ', '').replace('.', '').replace("'", '')}.gif"

    embed_color = discord.Colour.blue()  # Default color

    if pokemon.total_stats < 400:
        embed_color = discord.Colour.green()
    elif pokemon.total_stats < 500:
        embed_color = discord.Colour.blue()
    else:
        embed_color = discord.Colour.red()

    embed = discord.Embed(
        title=f"{ctx.author.display_name} picked {pokemon.name} with base stats:",
        color=embed_color
    )
    embed.set_image(url=gif_url)
    embed.add_field(name="HP", value=pokemon.hp, inline=True)
    embed.add_field(name="Attack", value=pokemon.attack, inline=True)
    embed.add_field(name="Defense", value=pokemon.defense, inline=True)
    embed.add_field(name="Special Attack", value=pokemon.sp_attack, inline=True)
    embed.add_field(name="Special Defense", value=pokemon.sp_defense, inline=True)
    embed.add_field(name="Speed", value=pokemon.speed, inline=True)
    embed.add_field(name="Total base power", value=pokemon.total_stats, inline=False)
    await ctx.send(embed=embed)

    if ctx.author == game['challenger']:
        game['challenger_pokemon'] = pokemon
    else:
        game['opponent_pokemon'] = pokemon

    if game['challenger_pokemon'] is not None and game['opponent_pokemon'] is not None:
        challenger_pokemon = game['challenger_pokemon']
        opponent_pokemon = game['opponent_pokemon']
        await ctx.send(f"Challenger's Pokémon: {challenger_pokemon.name} with total base power: {challenger_pokemon.total_stats}")
        await ctx.send(f"Challenged User's Pokémon: {opponent_pokemon.name} with total base power: {opponent_pokemon.total_stats}")
        if challenger_pokemon.total_stats > opponent_pokemon.total_stats:
            await ctx.send(f"{game['challenger'].mention} wins!")
        elif challenger_pokemon.total_stats < opponent_pokemon.total_stats:
            await ctx.send(f"{game['opponent'].mention} wins!")
        else:
            await ctx.send("It's a tie!")
        del ongoing_games[ctx.channel.id]

@client.command(name='deathroll')
async def deathroll(ctx, *, args: str = None):
    if not args:
        await ctx.send("❌ You must mention someone to challenge. Example: `.deathroll @user`")
        return

    mention = None

    for word in args.split():
        if word.startswith('<@') and word.endswith('>'):
            mention = word
            break

    if not mention:
        await ctx.send("❌ You must mention someone to challenge. Example: `.deathroll @user`")
        return

    try:
        opponent_id = int(mention.replace('<@!', '').replace('<@', '').replace('>', ''))
        opponent = await ctx.guild.fetch_member(opponent_id)
    except:
        await ctx.send("❌ Could not identify the opponent. Please mention them correctly.")
        return

    if ctx.channel.id in ongoing_games and ongoing_games[ctx.channel.id]['type'] == 'deathroll':
        await ctx.send("A deathroll game is already ongoing in this channel. Use `.stop` to stop the current game.")
        return

    ongoing_games[ctx.channel.id] = {
        'type': 'deathroll',
        'challenger': ctx.author,
        'opponent': opponent,
        'max_number': 1000,
        'turn': ctx.author
    }

    await ctx.send(f"{ctx.author.mention} has challenged {opponent.mention} to a Deathroll game! Starting at 1000. {ctx.author.mention} goes first. Use `.roll` to roll.")


@client.command(name='roll')
async def roll(ctx):
    if ctx.channel.id not in ongoing_games or ongoing_games[ctx.channel.id]['type'] != 'deathroll':
        await ctx.send("There is no deathroll game ongoing in this channel.")
        return

    game = ongoing_games[ctx.channel.id]

    if ctx.author != game['turn']:
        await ctx.send("It's not your turn to roll.")
        return

    roll_result = random.randint(1, game['max_number'])
    await ctx.send(f"{ctx.author.mention} rolled a {roll_result}!")

    if roll_result == 1:
        await ctx.send(f"💀 {ctx.author.mention} rolled a 1 and **loses** the game!")
        await ctx.send("https://tenor.com/view/sarcastic-smile-gif-5658090525017151947")

        del ongoing_games[ctx.channel.id]
        return

    # Continue the game
    game['max_number'] = roll_result
    game['turn'] = game['challenger'] if game['turn'] == game['opponent'] else game['opponent']
    await ctx.send(f"{game['turn'].mention}, it's your turn to roll with max number {roll_result}!")

@client.command(name='stop')
async def stop(ctx):
    # Check if the author has the Officers role
    if OFFICERS_ROLE_ID not in [role.id for role in ctx.author.roles]:
        await ctx.send("⛔ You cannot use this command. Ask **Shek** to give you access.")
        return

    channel_id = ctx.channel.id
    cleared = False  

    for game_dict in [ongoing_games, games, active_games, russian_roulette_games]:
        if channel_id in game_dict:
            del game_dict[channel_id]
            cleared = True

    if cleared:
        await ctx.send("🛑 All games in this channel have been stopped.")
    else:
        await ctx.send("There are no games currently running in this channel.")
@client.command(name='servers')
async def servers(ctx):
    guilds = client.guilds
    if guilds:
        await ctx.send("The bot is in the following servers:\n" + "\n".join([guild.name for guild in guilds]))
    else:
        await ctx.send("The bot is not in any servers.")

@client.command(name='shutdown')
async def shutdown(ctx):
    print(f"Author ID: {ctx.author.id}")
    print(f"Authorized User IDs: {authorized_users}")

    if ctx.author.id in authorized_users:
        await ctx.send("Shutting down...")
        gif_url = "https://tenor.com/view/3-2-1-fish-321-split-3-2-1-split-gif-13398731845865633130"

        # Send the GIF separately
        await ctx.send(gif_url)

        await client.close()  # This closes the bot connection to Discord
    else:
        print(f"Unauthorized attempt by User ID: {ctx.author.id}")
        await ctx.send("You do not have permission to use this command.")


@client.command()
async def help(ctx):
    embed = discord.Embed(
        title="📜 Bot Commands",
        description="Here are the available commands:",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="🔹 `.randoms`", value="Play a Random Pokemon match with another user.", inline=False)
    embed.add_field(name="🔹 `.flip`", value="Gamble by flipping a coin.", inline=False)
    embed.add_field(name="🔹 `.Jackpot`", value="A random user will be selected among all the participants. Need High luck.", inline=False)
    embed.add_field(name="🔹 `.russia`", value="OG Shek's russian roulette.", inline=False)
    embed.add_field(name="🔹 `.deathroll`", value="Game is played by rolling random numbers, whoever roll 1 loses the game.", inline=False)
    embed.add_field(name="🔹 `.crack`", value="Guessing game that is played in a duel.", inline=False)
    embed.add_field(name="🔹 `.shutdown`", value="Shutdown the bot (Only Shekhar786 :v)", inline=False)
    embed.add_field(name="🔹 `.servers`", value="List the servers bot is active in.", inline=False)
    
    embed.set_footer(text="Use .command to execute any of the above commands.")
    
    await ctx.send(embed=embed)
    
@client.command(name='russian')
async def russian(ctx):
    if ctx.channel.id in ongoing_games:
        await ctx.send("A game is already ongoing in this channel!")
        return

    message = await ctx.send("React with 🎯 within 10 seconds to join Russian Roulette!")
    await message.add_reaction("🎯")
    
    await asyncio.sleep(10)
    message = await ctx.channel.fetch_message(message.id)
    reaction = discord.utils.get(message.reactions, emoji="🎯")
    
    players = []
    if reaction:
        async for user in reaction.users():
            if user != client.user:
                players.append(user)
    
    if len(players) < 2:
        await ctx.send("Not enough players joined. Game canceled.")
        return
    
    random.shuffle(players)  # Shuffle for randomness
    ongoing_games[ctx.channel.id] = {
        'players': players, 
        'active': True, 
        'turn_order': players.copy(),  # Maintain turn order
        'eliminated': []
    }
    
    # Start the game
    await ctx.send(f"Game started! {', '.join(player.mention for player in players)} type `.in` one by one!")

    # First player goes
    current_player = ongoing_games[ctx.channel.id]['turn_order'][0]
    await ctx.send(f"{current_player.mention}, it's your turn to type `.in`!")

@client.command(name='in')
async def in_command(ctx):
    if ctx.channel.id not in ongoing_games or not ongoing_games[ctx.channel.id]['active']:
        await ctx.send("No active Russian Roulette game in this channel.")
        return

    game = ongoing_games[ctx.channel.id]
    turn_order = game['turn_order']

    # Get the player whose turn it is
    current_player = turn_order[0]

    if ctx.author != current_player:
        await ctx.send(f"It's {current_player.mention}'s turn! Please wait for your turn.")
        return

    # Roll to determine if the player survives or is eliminated
    eliminated_roll = random.choice([True, False])

    if eliminated_roll:
        # Eliminate the player
        game['eliminated'].append(ctx.author)
        game['players'].remove(ctx.author)
        turn_order.remove(ctx.author)  # Remove from turn order

        await ctx.send(f"💀 {ctx.author.mention} has been eliminated!")
    else:
        await ctx.send(f"{ctx.author.mention} survived! Next player's turn.")
        
    
    # Check if only one player remains
    if len(game['players']) == 1:
        winner = game['players'][0]
        await ctx.send(f"🏆 {winner.mention} wins the Russian Roulette game!")
        gif_url = "https://tenor.com/view/crazy-dance-dance-funny-dance-indian-dance-gif-10759205048433038"
        await ctx.send(gif_url)
        del ongoing_games[ctx.channel.id]
        return

    # Rotate the turn order to the next available player
    turn_order.append(turn_order.pop(0))  # Move current player to the end of the queue

    # Get the new current player
    next_player = turn_order[0]
    await ctx.send(f"{next_player.mention}, it's your turn to type `.in`!")
    
@client.tree.command(name="announce", description="Silently send a message or GIF to a specific channel")
@app_commands.describe(channel="The channel to send in", content="Message or GIF URL")
async def announce(interaction: discord.Interaction, channel: discord.TextChannel, content: str):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("You can't use this command.", ephemeral=True)
        return

    await channel.send(content)
    try:
        await interaction.response.defer(thinking=False)
    except discord.errors.InteractionResponded:
        pass  # If already responded somehow
        
@client.command()
async def crack(ctx, opponent: discord.Member):
    if ctx.author.id == opponent.id:
        await ctx.send("You can't play against yourself.")
        return
    if ctx.channel.id in games:
        await ctx.send("A game is already in progress in this channel!")
        return

    number = random.randint(1, 100)
    games[ctx.channel.id] = {
        "players": [ctx.author.id, opponent.id],
        "turn": ctx.author.id,
        "number": number
    }
    await ctx.send(f"🎯 Game started between {ctx.author.mention} and {opponent.mention}!\n"
                   f"{ctx.author.mention}, it's your turn. Guess a number between 1 and 100 using `.guess <number>`.")
                 
    if ctx.author.id == OWNER_ID or opponent.id == OWNER_ID:
     try:
        dev_user = await client.fetch_user(OWNER_ID)  # Safely fetch the user
        await dev_user.send(f"🔍 The number for the game in #{ctx.channel.name} is: **{number}**")
     except discord.Forbidden:
         pass  # Silently fail if DMs are disabled




@client.command()
async def guess(ctx, number: int):
    game = games.get(ctx.channel.id)

    if not game:
        await ctx.send("No game is active in this channel. Start one with `.crack @user`.")
        return

    if ctx.author.id not in game["players"]:
        await ctx.send("You're not a part of this game.")
        return

    if ctx.author.id != game["turn"]:
        await ctx.send(f"It's not your turn, <@{ctx.author.id}>.")
        return

    if number < 1 or number > 100:
        await ctx.send("Guess must be between 1 and 100.")
        return

    target = game["number"]

    if number == target:
        await ctx.send(f"🎉 {ctx.author.mention} cracked the number `{number}` and wins the game!")
        del games[ctx.channel.id]
    else:
        hint = "more than" if number < target else "less than"
        await ctx.send(f"❌ Nope! The hidden number is {hint} `{number}`.")

        # Switch turn
        next_player = [p for p in game["players"] if p != ctx.author.id][0]
        game["turn"] = next_player
        await ctx.send(f"It's now <@{next_player}>'s turn.")

@client.command(name="jackcrack")
async def jackcrack(ctx):
    # Initial embed for joining
    embed = discord.Embed(
        title="🎰 Jackpot Hardcore 🎰",
        description=(
            "React with 🎰 to join the game!\n\n"
            "➡️ Each player will pick **5 unique numbers** between **1–555**.\n"
            "🎯 If nobody matches the winning number, the **closest guess wins!**"
        ),
        color=discord.Color.gold()
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎰")

    # Wait 20 seconds for players
    await asyncio.sleep(20)
    msg = await ctx.channel.fetch_message(msg.id)  # refetch updated reactions

    # Collect players
    players = []
    async for user in msg.reactions[0].users():
        if not user.bot:
            players.append(user)

    if len(players) < 2:
        await ctx.send("❌ Not enough players joined. Game cancelled.")
        return

    player_choices = {}
    for player in players:
        await ctx.send(f"🎲 {player.mention}, it's your turn!\n"
                       "Please type **5 different numbers between 1–555 (comma separated).**")

        def check(m):
            return m.author == player and m.channel == ctx.channel

        valid = False
        while not valid:
            try:
                msg = await client.wait_for("message", check=check, timeout=60.0)

                # Safe parsing: strip spaces, ignore empties
                raw_nums = [x.strip() for x in msg.content.split(",")]
                try:
                    nums = [int(x) for x in raw_nums if x]
                except ValueError:
                    await ctx.send("⚠️ Invalid input! Please enter only numbers separated by commas.")
                    continue

                # Validation: 5 unique numbers in range
                if len(nums) == 5 and len(set(nums)) == 5 and all(1 <= n <= 555 for n in nums):
                    player_choices[player] = nums
                    valid = True
                else:
                    await ctx.send("⚠️ Invalid input! Enter **5 unique numbers between 1–1000**, separated by commas.")
            except asyncio.TimeoutError:
                await ctx.send(f"⏰ {player.mention} took too long. Skipping their turn.")
                break

    if not player_choices:
        await ctx.send("❌ No valid entries. Game cancelled.")
        return

    # Generate winning number
    winning_number = random.randint(1, 555)

    # Determine winners
    winners = [p for p, nums in player_choices.items() if winning_number in nums]
    if winners:
        result_text = "🎉 **Exact Match Winner(s):**\n" + "\n".join([p.mention for p in winners])
    else:
        closest_player = min(
            player_choices.items(),
            key=lambda x: min(abs(n - winning_number) for n in x[1])
        )[0]
        result_text = f"🤏 No exact match.\nClosest winner: {closest_player.mention}"

    # Build final results embed
    final_embed = discord.Embed(
        title="🏆 Jackpot Results 🏆",
        description=f"🎯 Winning Number: **{winning_number}**\n\n{result_text}",
        color=discord.Color.green()
    )

    for player, nums in player_choices.items():
        final_embed.add_field(name=player.display_name, value=", ".join(map(str, nums)), inline=False)

    await ctx.send(embed=final_embed)


TOKEN = os.getenv("TOKEN")
client.run(TOKEN)

