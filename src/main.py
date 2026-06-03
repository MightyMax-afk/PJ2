#!/usr/bin/env python3
"""
Classic Turn-Based RPG — main entry point.
Inspired by Final Fantasy / Breath of Fire.
"""
from __future__ import annotations
import random
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from character import make_warrior, make_mage, make_rogue, make_healer
from party import Party
from enemy import random_encounter
from items import ITEMS
from skills import SKILLS, SkillType, TargetType
from battle import Battle, BattleAction, BattleResult
from save_load import save_game, load_game
import ui


ZONES = ["forest", "cave", "dungeon"]


# ── Battle loop ────────────────────────────────────────────────────────────────

def player_turn(character, party, enemies, battle: Battle) -> BattleAction | None:
    ui.print_battle_header(party.members, enemies)

    action_key = ui.battle_menu(character)

    if action_key == "attack":
        skill = SKILLS["attack"]
        alive_enemies = battle.active_enemies
        if len(alive_enemies) == 1:
            target = alive_enemies[0]
        else:
            idx = ui.choose_target("Target:", alive_enemies)
            target = alive_enemies[idx]
        return BattleAction(actor=character, action_type="skill", skill=skill, targets=[target])

    if action_key == "skill":
        known = [SKILLS[sid] for sid in character.skill_list if sid in SKILLS]
        known_strs = [str(s) for s in known]
        idx = ui.choose("Choose skill:", known_strs, allow_back=True)
        if idx == -1:
            return player_turn(character, party, enemies, battle)
        skill = known[idx]

        # Resolve targets
        if skill.target == TargetType.SINGLE_ENEMY:
            alive = battle.active_enemies
            tidx = ui.choose_target("Target:", alive) if len(alive) > 1 else 0
            targets = [alive[tidx]]
        elif skill.target == TargetType.ALL_ENEMIES:
            targets = battle.active_enemies
        elif skill.target == TargetType.SINGLE_ALLY:
            alive = battle.active_party
            tidx = ui.choose_target("Target:", alive) if len(alive) > 1 else 0
            targets = [alive[tidx]]
        elif skill.target == TargetType.ALL_ALLIES:
            targets = battle.active_party
        else:
            targets = [character]
        return BattleAction(actor=character, action_type="skill", skill=skill, targets=targets)

    if action_key == "item":
        inv = party.inventory
        if not inv.items:
            print("  You have no items!")
            return player_turn(character, party, enemies, battle)
        item_options = [f"{ITEMS[iid].name} x{qty}" for iid, qty in inv.items.items()]
        item_ids = list(inv.items.keys())
        idx = ui.choose("Use item:", item_options, allow_back=True)
        if idx == -1:
            return player_turn(character, party, enemies, battle)
        item_id = item_ids[idx]
        item = ITEMS[item_id]

        if item.revive:
            ko_members = [m for m in party.members if m.is_ko]
            if not ko_members:
                print("  No one to revive!")
                return player_turn(character, party, enemies, battle)
            tidx = ui.choose_target("Revive:", ko_members) if len(ko_members) > 1 else 0
            target = ko_members[tidx]
        else:
            alive = battle.active_party
            tidx = ui.choose_target("Use on:", alive) if len(alive) > 1 else 0
            target = alive[tidx]

        inv.remove(item_id)
        return BattleAction(actor=character, action_type="item", item_id=item_id, targets=[target])

    if action_key == "defend":
        return BattleAction(actor=character, action_type="defend", targets=[character])

    if action_key == "run":
        return BattleAction(actor=character, action_type="run", targets=[])

    return None


def run_battle(party: Party, enemies) -> BattleResult:
    battle = Battle(party.members, enemies)

    print("\n" + "=" * 60)
    print("  ENEMY APPEARS!")
    for e in enemies:
        print(f"    A wild {e.name} appears!")
    ui.pause()

    while battle.check_result() == BattleResult.ONGOING:
        battle.round += 1
        print(f"\n  ── Round {battle.round} ──")

        order = battle.turn_order()

        for combatant in order:
            if battle.check_result() != BattleResult.ONGOING:
                break
            if not combatant.is_alive:
                continue

            from character import Character
            from enemy import Enemy

            if isinstance(combatant, Character):
                action = player_turn(combatant, party, enemies, battle)
                if action:
                    msgs = battle.execute_action(action)
                    ui.print_messages(msgs)
            elif isinstance(combatant, Enemy):
                msgs = battle.enemy_turn(combatant)
                ui.print_messages(msgs)

        # End-of-round status ticks
        tick_msgs = battle.tick_statuses()
        if tick_msgs:
            ui.print_messages(tick_msgs)

    # Battle over
    result = battle.check_result()
    if result == BattleResult.VICTORY:
        exp, gold, drops = battle.collect_rewards()
        print(f"\n  VICTORY!")
        print(f"  Gained {exp} EXP and {gold} Gold!")
        party.add_gold(gold)
        for item_id in drops:
            item = ITEMS.get(item_id)
            name = item.name if item else item_id
            party.inventory.add(item_id)
            print(f"  Found: {name}!")
        print()
        for member in party.active:
            level_msgs = member.gain_exp(exp)
            for msg in level_msgs:
                print(f"  {msg}")
        ui.pause()

    elif result == BattleResult.DEFEAT:
        print("\n  DEFEAT... The party has fallen.")
        ui.pause()

    elif result == BattleResult.ESCAPED:
        print("\n  The party fled!")
        ui.pause()

    return result


# ── Overworld loop ─────────────────────────────────────────────────────────────

def overworld_menu(party: Party, zone: str) -> str:
    ui.header(f"OVERWORLD — {zone.upper()}")
    print(party.summary())
    options = [
        "Explore (random encounter)",
        "Check inventory",
        "Rest (full HP/MP restore)",
        "Change zone",
        "Save game",
        "Quit",
    ]
    idx = ui.choose("What will you do?", options)
    return ["explore", "inventory", "rest", "zone", "save", "quit"][idx]


def run_overworld(party: Party, start_zone: str = "forest") -> None:
    zone_ref = [start_zone]

    while True:
        action = overworld_menu(party, zone_ref[0])

        if action == "explore":
            if party.is_wiped:
                print("  Your party is wiped out. Rest first!")
                continue
            enemies = random_encounter(zone_ref[0])
            result = run_battle(party, enemies)
            if result == BattleResult.DEFEAT:
                print("  GAME OVER")
                if ui.choose("Continue?", ["Yes — load last save", "No — quit"]) == 0:
                    load_game(party, zone_ref)
                else:
                    sys.exit(0)

        elif action == "inventory":
            ui.header("INVENTORY")
            print(party.inventory_summary())
            ui.pause()

        elif action == "rest":
            party.rest()
            print("  The party rests and recovers fully.")
            ui.pause()

        elif action == "zone":
            idx = ui.choose("Travel to zone:", ZONES)
            zone_ref[0] = ZONES[idx]
            print(f"  Traveling to {ZONES[idx]}...")
            ui.pause()

        elif action == "save":
            save_game(party, zone_ref[0])
            ui.pause()

        elif action == "quit":
            print("  Thanks for playing!")
            sys.exit(0)


# ── Title screen ───────────────────────────────────────────────────────────────

def title_screen() -> str:
    ui.header("CHRONICLE OF ECHOES")
    print("""
        A classic turn-based RPG
        ─────────────────────────
    """)
    idx = ui.choose("Main Menu", ["New Game", "Load Game", "Quit"])
    return ["new", "load", "quit"][idx]


def main() -> None:
    party = Party(
        members=[make_warrior(), make_mage(), make_rogue(), make_healer()],
        gold=200,
    )
    # Starter items
    party.inventory.add("potion", 3)
    party.inventory.add("ether", 2)
    party.inventory.add("antidote", 2)

    zone_ref = ["forest"]

    choice = title_screen()

    if choice == "new":
        print("\n  A new adventure begins...")
        ui.pause()
        run_overworld(party, zone_ref[0])

    elif choice == "load":
        if load_game(party, zone_ref):
            run_overworld(party, zone_ref[0])
        else:
            ui.pause()
            run_overworld(party, zone_ref[0])

    elif choice == "quit":
        print("  Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
