from dataclasses import dataclass, field
from character import Character
from items import Inventory, ITEMS


@dataclass
class Party:
    members: list[Character]
    inventory: Inventory = field(default_factory=Inventory)
    gold: int = 0
    max_size: int = 4

    @property
    def active(self) -> list[Character]:
        return [m for m in self.members if m.is_alive]

    @property
    def is_wiped(self) -> bool:
        return all(m.is_ko for m in self.members)

    def add_gold(self, amount: int) -> None:
        self.gold += amount

    def spend_gold(self, amount: int) -> bool:
        if self.gold < amount:
            return False
        self.gold -= amount
        return True

    def rest(self) -> None:
        """Full HP/MP restore and clear all status effects (inn / save point)."""
        for m in self.members:
            m.hp = m.stats.max_hp
            m.mp = m.stats.max_mp
            m.status_effects.clear()

    def summary(self) -> str:
        lines = [f"  Gold: {self.gold}G", ""]
        for m in self.members:
            status = " [KO]" if m.is_ko else m.status_str()
            lines.append(
                f"  {m.name:<10} Lv{m.level:<3} "
                f"HP:{m.hp:>4}/{m.stats.max_hp:<4} "
                f"MP:{m.mp:>3}/{m.stats.max_mp:<3}"
                f"{status}"
            )
        return "\n".join(lines)

    def inventory_summary(self) -> str:
        if not self.inventory.items:
            return "  (empty)"
        lines = []
        for item_id, qty in self.inventory.items.items():
            item = ITEMS.get(item_id)
            name = item.name if item else item_id
            lines.append(f"  {name:<18} x{qty}")
        return "\n".join(lines)
