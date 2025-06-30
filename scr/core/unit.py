# real_time_chess/src/core/entities/unit.py

# Import global constants if defined in src.utils.constants
# from ...utils.constants import UNIT_ARCHETYPES, GAME_TICK_RATE
# For this skeletal file, we'll temporarily define UNIT_ARCHETYPES here
# to make it runnable independently for testing the class logic.

# Placeholder for UNIT_ARCHETYPES (will eventually be loaded from data/unit_archetypes.json)
UNIT_ARCHETYPES = {
    "Pawn": {"hp": 10, "attack": 2, "defense": 1, "speed": 1, "sight_range": 2, "abilities": []},
    "Rook": {"hp": 30, "attack": 5, "defense": 4, "speed": 0.5, "sight_range": 3, "abilities": []},
    "Knight": {"hp": 15, "attack": 3, "defense": 2, "speed": 1.5, "sight_range": 2, "abilities": []},
    "Bishop": {"hp": 12, "attack": 2, "defense": 1, "speed": 1, "sight_range": 4, "abilities": []},
    "Queen": {"hp": 40, "attack": 7, "defense": 5, "speed": 1.2, "sight_range": 5, "abilities": []},
    "King": {"hp": 50, "attack": 1, "defense": 3, "speed": 0.8, "sight_range": 6, "abilities": []},
}

class Unit:
    """
    Represents a single military unit on the battlefield.
    This class handles the unit's core attributes, state, and basic interactions.
    """
    def __init__(self, unit_id: str, player_id: str, unit_type: str, position: list):
        """
        Initializes a new unit.

        Args:
            unit_id (str): A unique identifier for this specific unit instance.
            player_id (str): The ID of the player who owns this unit.
            unit_type (str): The archetype name of the unit (e.g., "Pawn", "Rook").
            position (list): The [x, y] coordinates of the unit on the board.
        """
        self.id = unit_id
        self.player_id = player_id
        self.unit_type = unit_type
        self.position = list(position) # Ensure it's a mutable list
        self.is_alive = True
        self.morale = 100 # Initial morale, can be affected by combat/cards
        self.current_orders = [] # A list/queue of orders the unit needs to execute
        self.behavior_patterns = {} # Dictionary to store assigned behavior patterns (e.g., movement, engagement)

        # Load attributes from the archetype definition
        archetype_data = UNIT_ARCHETYPES.get(unit_type)
        if not archetype_data:
            raise ValueError(f"Unknown unit type: {unit_type}. Please define it in UNIT_ARCHETYPES.")

        self.hp = archetype_data["hp"]
        self.max_hp = archetype_data["hp"] # Store max HP for reference
        self.attack = archetype_data["attack"]
        self.defense = archetype_data["defense"]
        self.speed = archetype_data["speed"] # Tiles per game tick or per second
        self.sight_range = archetype_data["sight_range"]
        self.abilities = archetype_data["abilities"] # List of special abilities

        self.is_king = False # Default for a regular unit

    def update(self, game_state):
        """
        Updates the unit's state each game tick.
        This is where movement, order execution, and AI behavior would be processed.

        Args:
            game_state: A reference to the main Game object to access other modules.
        """
        if not self.is_alive:
            return

        # TODO: Implement unit's movement logic based on 'self.speed' and 'self.current_orders'
        # Example: Move towards the target of the first order in current_orders
        if self.current_orders:
            first_order = self.current_orders[0]
            if first_order.get("type") == "move_to":
                target_pos = first_order.get("target_pos")
                if target_pos and self.position != target_pos:
                    # Very simple direct movement simulation for now
                    # In a real game, this would involve step-by-step movement, pathfinding
                    # and considering movement speed and terrain.
                    old_pos = list(self.position)
                    if self.position[0] < target_pos[0]:
                        self.position[0] += 1
                    elif self.position[0] > target_pos[0]:
                        self.position[0] -= 1

                    if self.position[1] < target_pos[1]:
                        self.position[1] += 1
                    elif self.position[1] > target_pos[1]:
                        self.position[1] -= 1

                    if self.position == target_pos:
                        print(f"Unit {self.id} reached target {target_pos}.")
                        self.current_orders.pop(0) # Remove completed order
                    else:
                        # Inform battlefield module about position change
                        # This would be more complex with actual movement over time
                        # For now, a simplified update
                        # game_state.battlefield_module.update_unit_position_on_grid(self.id, old_pos, self.position)
                        pass # Deferred until actual movement system is in place
                else:
                    self.current_orders.pop(0) # Target reached or invalid
            # TODO: Add logic for other order types (e.g., "attack_unit")

        # TODO: Implement behavior pattern execution (e.g., if no active orders, follow 'aggressive' pattern)
        # TODO: Implement logic for units to find and engage nearby enemies (within engagement range)

    def receive_damage(self, amount: int):
        """
        Reduces the unit's health points and checks if the unit is defeated.

        Args:
            amount (int): The amount of damage to inflict.
        """
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
            print(f"Unit {self.id} ({self.unit_type}) of player {self.player_id} has been defeated!")
        else:
            print(f"Unit {self.id} took {amount} damage. HP: {self.hp}/{self.max_hp}")

    def is_defeated(self) -> bool:
        """Checks if the unit has been defeated (HP <= 0)."""
        return not self.is_alive

    # TODO: Add methods for special abilities, morale changes, status effects


class King(Unit):
    """
    Specialized Unit class for the King, representing the player's Headquarters (HQ).
    The King has additional properties related to command and visibility.
    """
    def __init__(self, unit_id: str, player_id: str, position: list):
        """
        Initializes a new King unit.

        Args:
            unit_id (str): A unique identifier for this specific King instance.
            player_id (str): The ID of the player who owns this King.
            position (list): The [x, y] coordinates of the King on the board.
        """
        super().__init__(unit_id, player_id, "King", position)
        self.is_king = True
        # The King's sight_range is also its headquarters' direct visual range
        self.hq_visual_range = self.sight_range

    def move_king(self, new_position: list):
        """
        Allows the player to move their King unit.
        This also implicitly affects messenger travel times and HQ visibility.

        Args:
            new_position (list): The new [x, y] coordinates for the King.
        """
        # TODO: Add validation for new_position (e.g., within board bounds, no obstacles)
        old_pos = list(self.position)
        self.position = list(new_position)
        print(f"King of player {self.player_id} moved from {old_pos} to {self.position}")

        # In a full implementation, you'd inform the battlefield module to update its internal
        # representation of unit positions. For now, it's just updating the unit's internal position.
        # game_state.battlefield_module.update_unit_position_on_grid(self.id, old_pos, self.position)


# Example usage (for testing this file directly)
if __name__ == "__main__":
    print("--- Testing Unit and King Classes ---")

    # Create a dummy game state for testing purposes
    class MockBattlefield:
        def is_within_bounds(self, pos):
            return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

    class MockGame:
        def __init__(self):
            self.battlefield_module = MockBattlefield()
            # Minimalist mock for update calls
            print("MockGame initialized.")

    mock_game = MockGame()

    # Create some units
    pawn1 = Unit("pawn_alpha", "player1", "Pawn", [1, 1])
    knight1 = Unit("knight_beta", "player1", "Knight", [3, 3])
    king1 = King("king_player1", "player1", [0, 0])

    pawn2 = Unit("pawn_gamma", "player2", "Pawn", [6, 6])
    king2 = King("king_player2", "player2", [7, 7])

    print("\nInitial Unit States:")
    print(f"{pawn1.id}: HP={pawn1.hp}, Pos={pawn1.position}, Speed={pawn1.speed}")
    print(f"{king1.id}: HP={king1.hp}, Pos={king1.position}, Sight={king1.hq_visual_range}")

    # Simulate damage
    print("\nSimulating damage to pawn_alpha:")
    pawn1.receive_damage(5)
    pawn1.receive_damage(7) # Should defeat it

    print("\nSimulating King movement:")
    king1.move_king([2, 2])
    print(f"King {king1.id} new position: {king1.position}")

    # Simulate an order for a unit
    print("\nSimulating order for knight_beta to move:")
    knight1.current_orders.append({"type": "move_to", "target_pos": [5, 5]})
    print(f"Knight {knight1.id} orders: {knight1.current_orders}")

    # Simulate a few game ticks to see movement
    print("\nSimulating game ticks for knight_beta movement:")
    for _ in range(5):
        knight1.update(mock_game)
        print(f"Knight {knight1.id} at {knight1.position} after tick.")

    print("\n--- End of Unit and King Class Test ---")
