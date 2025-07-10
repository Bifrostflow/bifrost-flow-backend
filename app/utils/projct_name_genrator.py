import random

def generate_norse_project_name():
    # Prefix concepts (places, weapons, ideas)
    prefixes = [
        "Valhalla", "Ragnarok", "Yggdrasil", "Bifrost", "Gjallar",
        "Jotun", "Runestone", "Valkyrie", "Valknut", "Frostborn",
        "Leviathan", "Muspel", "Nifl", "Aether", "Draupnir", "Eclipse",
        "Mythforge", "Stormrune", "Ashen", "Saga"
    ]

    # Suffix concepts (abstract ideas, materials, realms, power)
    suffixes = [
        "Forge", "Runes", "Fire", "Flame", "Vault", "Path", "Flow",
        "Bound", "Realm", "Gate", "Sync", "Rise", "Quest", "Pulse",
        "Echo", "Drift", "Hollow", "Blaze", "Seal", "Verse"
    ]

    name = f"{random.choice(prefixes)} {random.choice(suffixes)}"
    return name