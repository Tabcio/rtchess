# real_time_chess/src/modules/combat_module.py

import random

# You might eventually import the Unit class if needed for type hinting or direct access,
# but for the core combat logic, units are passed as arguments.
# from ..core.entities.unit import Unit # Uncomment if needed

class CombatModule:
    """
    Manages all combat calculations and resolutions between units.
    This module handles engagement, damage calculation, and applying combat effects.
    """
    def __init__(self):
        """
        Initializes the CombatModule.
        Stores a list of all active combat engagements currently happening on the battlefield.
        """
        # Each engagement can be a tuple or a custom CombatInstance object: (unit_a, unit_b)
        self.active_engagements = []
        print("CombatModule initialized.")

    def initiate_combat(self, unit_a, unit_b):
        """
        Initiates a combat encounter between two units.
        This method adds a new engagement to the list of active combats.

        Args:
            unit_a: The first unit involved in the combat.
            unit_b: The second unit involved in the combat.
        """
        # Ensure units are alive and from opposing players before initiating combat
        if unit_a.is_alive and unit_b.is_alive and unit_a.player_id != unit_b.player_id:
            if (unit_a, unit_b) not in self.active_engagements and (unit_b, unit_a) not in self.active_engagements:
                self.active_engagements.append((unit_a, unit_b))
                print(f"Combat initiated between {unit_a.id} ({unit_a.unit_type}) and {unit_b.id} ({unit_b.unit_type})!")
            else:
                # print(f"Combat already active between {unit_a.id} and {unit_b.id}.")
                pass # Combat already ongoing
        else:
            print(f"Cannot initiate combat: Units not alive or same player ({unit_a.id} vs {unit_b.id}).")

    def resolve_combat_tick(self, unit_a, unit_b, battlefield_module) -> bool:
        """
        Applies one tick of combat resolution between two engaged units.
        This includes damage calculation, application of modifiers, and checking for unit defeat.

        Args:
            unit_a: The first unit in the engagement.
            unit_b: The second unit in the engagement.
            battlefield_module: Reference to the BattlefieldModule for terrain info, etc.

        Returns:
            bool: True if both units are still alive and combat should continue, False otherwise.
        """
        if not unit_a.is_alive or not unit_b.is_alive:
            return False # One or both units are already defeated, combat ends

        # --- Base Damage Calculation ---
        # Raw damage is capped at 0 to prevent healing from negative attack-defense
        damage_a_to_b = max(0, unit_a.attack - unit_b.defense)
        damage_b_to_a = max(0, unit_b.attack - unit_a.defense)

        # --- Apply Modifiers (Placeholder for future expansion) ---
        # TODO: Incorporate terrain modifiers (from battlefield_module)
        # terrain_a = battlefield_module.get_terrain_at(unit_a.position)
        # terrain_b = battlefield_module.get_terrain_at(unit_b.position)
        # damage_a_to_b *= terrain_b.get("combat_modifier", 1.0) # Example: terrain of defender affects damage taken

        # TODO: Incorporate morale effects
        # if unit_a.morale < 50: damage_a_to_b *= 0.8 # Example: low morale reduces damage dealt

        # TODO: Incorporate card effects (from active_card_effects in CardSystemModule)
        # (This would likely be handled by the card system module itself applying temporary buffs/debuffs to unit stats)

        # TODO: Incorporate special abilities

        # --- Non-Deterministic Outcome (Randomness) ---
        # Simple hit chance
        hit_chance = 0.8 # 80% chance to hit

        if random.random() < hit_chance:
            unit_b.receive_damage(damage_a_to_b)
        else:
            print(f"{unit_a.id} missed {unit_b.id}!")

        if unit_b.is_alive and random.random() < hit_chance: # Only if B is still alive to retaliate
            unit_a.receive_damage(damage_b_to_a)
        elif not unit_b.is_alive:
            print(f"{unit_b.id} was defeated before retaliating.")
        else:
            print(f"{unit_b.id} missed {unit_a.id}!")

        # Check if both units are still alive after this tick
        return unit_a.is_alive and unit_b.is_alive

    def update_combat(self, game_state):
        """
        Updates all active combat engagements for the current game tick.
        Engagements where one or both units are defeated are removed.

        Args:
            game_state: A reference to the main Game object to access other modules
                        (e.g., unit_module, battlefield_module).
        """
        engagements_to_keep = []
        for unit_a, unit_b in list(self.active_engagements): # Iterate over a copy
            # Ensure units still exist in the unit_module (haven't been removed as defeated already)
            # This handles cases where a unit might have been defeated by something else
            # (e.g., a card effect, or if its HP dropped below 0 from prior combat resolution)
            if (game_state.unit_module.get_unit_by_id(unit_a.id) and
                game_state.unit_module.get_unit_by_id(unit_b.id) and
                unit_a.is_alive and unit_b.is_alive):
                if self.resolve_combat_tick(unit_a, unit_b, game_state.battlefield_module):
                    engagements_to_keep.append((unit_a, unit_b))
                else:
                    print(f"Combat between {unit_a.id} and {unit_b.id} concluded.")
            else:
                print(f"Combat between {unit_a.id} and {unit_b.id} ended prematurely (unit removed).")

        self.active_engagements = engagements_to_keep


# Example usage for testing this file directly
if __name__ == "__main__":
    print("--- Testing CombatModule ---")

    # Mock dependent classes for standalone testing
    class MockUnit:
        def __init__(self, unit_id, player_id, hp, attack, defense, position):
            self.id = unit_id
            self.player_id = player_id
            self.hp = hp
            self.max_hp = hp
            self.attack = attack
            self.defense = defense
            self.position = list(position)
            self.is_alive = True
            self.unit_type = "MockUnit" # For printing

        def receive_damage(self, amount):
            self.hp -= amount
            if self.hp <= 0:
                self.hp = 0
                self.is_alive = False
            print(f"  Unit {self.id} took {amount} damage. HP: {self.hp}/{self.max_hp}. Alive: {self.is_alive}")

    class MockUnitModule:
        # Simplified for combat module testing; just holds units
        def __init__(self):
            self.units = {}
        def get_unit_by_id(self, unit_id):
            return self.units.get(unit_id)

    class MockBattlefieldModule:
        # Minimalist mock for resolve_combat_tick argument
        def get_terrain_at(self, position):
            return {"combat_modifier": 1.0} # No actual terrain effects for now
        def is_within_bounds(self, pos):
            return True # Always within bounds for this mock

    class MockGame:
        def __init__(self):
            self.unit_module = MockUnitModule()
            self.battlefield_module = MockBattlefieldModule()
            print("MockGame initialized for CombatModule testing.")

    mock_game = MockGame()
    combat_manager = CombatModule()

    # Create mock units
    fighter_a = MockUnit("FighterA", "player1", 20, 5, 2, [1,1])
    fighter_b = MockUnit("FighterB", "player2", 15, 4, 1, [2,2])
    tank_c = MockUnit("TankC", "player2", 40, 2, 5, [3,3])

    # Add units to mock game's unit module so they can be looked up
    mock_game.unit_module.units[fighter_a.id] = fighter_a
    mock_game.unit_module.units[fighter_b.id] = fighter_b
    mock_game.unit_module.units[tank_c.id] = tank_c


    print("\nInitiating combat between FighterA and FighterB:")
    combat_manager.initiate_combat(fighter_a, fighter_b)

    print("\nSimulating combat ticks:")
    for i in range(1, 10):
        if not fighter_a.is_alive or not fighter_b.is_alive:
            print(f"Combat ended after {i-1} ticks.")
            break
        print(f"\n--- Combat Tick {i} ---")
        combat_manager.update_combat(mock_game)
        if not fighter_a.is_alive or not fighter_b.is_alive:
            print(f"Combat ended after {i} ticks.")
            break

    print(f"\nFinal state of FighterA: HP={fighter_a.hp}, Alive={fighter_a.is_alive}")
    print(f"Final state of FighterB: HP={fighter_b.hp}, Alive={fighter_b.is_alive}")

    # Test another combat where one unit is much stronger
    print("\nInitiating combat between FighterA (new) and TankC:")
    fighter_a_new = MockUnit("FighterA_New", "player1", 25, 6, 2, [1,1])
    mock_game.unit_module.units[fighter_a_new.id] = fighter_a_new # Add to mock unit module
    combat_manager.initiate_combat(fighter_a_new, tank_c)

    for i in range(1, 15):
        if not fighter_a_new.is_alive or not tank_c.is_alive:
            print(f"Combat ended after {i-1} ticks.")
            break
        print(f"\n--- Combat Tick {i} (FighterA_New vs TankC) ---")
        combat_manager.update_combat(mock_game)
        if not fighter_a_new.is_alive or not tank_c.is_alive:
            print(f"Combat ended after {i} ticks.")
            break

    print(f"\nFinal state of FighterA_New: HP={fighter_a_new.hp}, Alive={fighter_a_new.is_alive}")
    print(f"Final state of TankC: HP={tank_c.hp}, Alive={tank_c.is_alive}")


    print("\n--- End of CombatModule Test ---")
