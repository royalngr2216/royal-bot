from data.pokemon import POKEMON_LIST

# sort ascending by BST
POKEMON_LIST.sort(key=lambda p: p.total_stats)

print("POKEMON_LIST = [")
for p in POKEMON_LIST:
    print(f'    Pokemon("{p.name}", {p.hp}, {p.attack}, {p.defense}, {p.sp_attack}, {p.sp_defense}, {p.speed}),  # {p.total_stats}')
print("]")
