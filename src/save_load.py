"""Simple JSON save/load for party state."""
import json
import os
from typing import Any

SAVE_FILE = "savegame.json"


def save_game(party, current_zone: str) -> None:
    data: dict[str, Any] = {
        "zone": current_zone,
        "gold": party.gold,
        "inventory": party.inventory.items,
        "members": [],
    }
    for m in party.members:
        data["members"].append({
            "name": m.name,
            "level": m.level,
            "exp": m.exp,
            "hp": m.hp,
            "mp": m.mp,
            "skill_list": m.skill_list,
        })
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Game saved to {SAVE_FILE}.")


def load_game(party, zone_ref: list) -> bool:
    """Loads save data into an existing party object. Returns True if successful."""
    if not os.path.exists(SAVE_FILE):
        print("  No save file found.")
        return False
    with open(SAVE_FILE) as f:
        data = json.load(f)

    party.gold = data.get("gold", 0)
    party.inventory.items = data.get("inventory", {})
    zone_ref[0] = data.get("zone", "forest")

    saved_members = data.get("members", [])
    for saved, member in zip(saved_members, party.members):
        member.level = saved["level"]
        member.exp = saved["exp"]
        member.hp = saved["hp"]
        member.mp = saved["mp"]
        member.skill_list = saved["skill_list"]
        # Reapply stat scaling for current level
        for _ in range(1, member.level):
            member._level_up_stats()

    print(f"  Game loaded from {SAVE_FILE}.")
    return True
