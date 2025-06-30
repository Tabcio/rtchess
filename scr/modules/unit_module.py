# real_time_chess/src/modules/unit_module.py

# Import Unit and King classes from the entities sub-package
from ..core.entities.unit import Unit, King

# You would ideally load UNIT_ARCHETYPES from data/unit_archetypes.json
# For now, it's defined here as a placeholder for self-containment.
UNIT_ARCHETYPES = {
    "Pawn": {"hp": 10, "attack": 2, "defense": 1, "speed": 1, "sight_range": 2, "abilities": []},
    "Rook": {"hp": 30, "attack": 5, "defense": 4, "speed": 0.5, "sight_range": 3, "abilities": []},
    "Knight": {"hp": 15, "attack": 3, "defense": 2, "speed": 1.5, "sight_range": 2, "abilities": []},
    "Bishop": {"hp": 12, "attack": 2, "defense": 1, "speed": 1, "sight_range": 4, "abilities": []},
    "Queen": {"hp": 40, "attack": 7, "defense": 5, "speed": 1.2, "sight_range": 5, "abilities": []},
    "King": {"hp": 50, "attack": 1, "defense": 3, "speed": 0.8, "sight_range": 6, "abilities": []},
}

class UnitModule:
    """
    Manages all units in the game.
    Responsibilities include creating units, retrieving them, and updating their states.
    """
    def __init__(self):
        """
        Initializes the UnitModule.
        Stores all active units and a quick reference to King units by player ID.
        """
        self.units = {} # Dictionary to store all active Unit objects: {unit_id: Unit_object}
        self.player_kings = {} # Dictionary to store King unit references: {player_id: King_object}

    def create_unit(self, unit_id: str, player_id: str, unit_type: str, position: list) -> Unit:
        """
        Creates and registers a new unit instance.

        Args:
            unit_id (str): A unique identifier for the new unit.
            player_id (str): The ID of the player owning this unit.
            unit_type (str): The type of unit to create (e.g., "Pawn", "King").
            position (list): The initial [x, y] coordinates of the unit.

        Returns:
            Unit: The newly created Unit or King object, or None if the type is unknown.
        """
        unit_data = UNIT_ARCHETYPES.get(unit_type)
        if not unit_data:
            print(f"Error: Unknown unit type '{unit_type}'. Cannot create unit {unit_id}.")
            return None

        if unit_type == "King":
            unit = King(unit_id, player_id, position)
            self.player_kings[player_id] = unit
        else:
            unit = Unit(
                unit_id, player_id, unit_type, position,
            ) # Unit class handles loading attributes from archetype_data internally
        self.units[unit_id] = unit
        print(f"Created {unit_type} '{unit_id}' for player '{player_id}' at {position}.")
        return unit

    def get_unit_by_id(self, unit_id: str) -> Unit:
        """
        Retrieves a unit object by its unique identifier.

        Args:
            unit_id (str): The ID of the unit to retrieve.

        Returns:
            Unit: The Unit object if found, otherwise None.
        """
        return self.units.get(unit_id)

    def get_king_unit(self, player_id: str) -> King:
        """
        Retrieves the King unit for a specified player.

        Args:
            player_id (str): The ID of the player whose King is to be retrieved.

        Returns:
            King: The King object for the given player, or None if not found.
        """
        return self.player_kings.get(player_id)

    def get_units_by_player(self, player_id: str) -> list[Unit]:
        """
        Retrieves a list of all active units belonging to a specific player.

        Args:
            player_id (str): The ID of the player whose units are to be retrieved.

        Returns:
            list[Unit]: A list of Unit objects owned by the player and still alive.
        """
        return [unit for unit in self.units.values() if unit.player_id == player_id and unit.is_alive]

    def get_all_active_units(self) -> list[Unit]:
        """
        Retrieves a list of all active (not defeated) units in the game.

        Returns:
            list[Unit]: A list of all active Unit objects.
        """
        return [unit for unit in self.units.values() if unit.is_alive]

    def update_units(self, game_state):
        """
        Iterates through all active units and calls their individual update methods.
        Also handles removal of defeated units.

        Args:
            game_state: A reference to the main Game object to pass to unit updates.
        """
        units_to_remove = []
        for unit_id, unit in list(self.units.items()): # Iterate over a copy to allow modification during loop
            if unit.is_alive:
                unit.update(game_state)
                if not unit.is_alive:
                    units_to_remove.append(unit_id)
            else:
                units_to_remove.append(unit_id)

        for unit_id in units_to_remove:
            if unit_id in self.units:
                del self.units[unit_id]
                print(f"Removed defeated unit: {unit_id}.")
            if unit_id in self.player_kings and not self.player_kings[unit_id].is_alive:
                del self.player_kings[unit_id] # Remove king from quick lookup if defeated


# Example usage for testing this file directly
if __name__ == "__main__":
    print("--- Testing UnitModule ---")

    # Mock dependent classes for standalone testing
    class MockGame:
        def __init__(self):
            # A very minimal mock of the game state for unit.update to run
            # In a real scenario, game.py will pass a full Game object
            self.battlefield_module = None # Placeholder for later use in unit movement
            self.unit_module = self # Self-reference to simulate unit_module access if needed by units
            print("MockGame initialized for UnitModule testing.")

    mock_game = MockGame()
    unit_manager = UnitModule()
    mock_game.unit_module = unit_manager # Ensure the mock game has access to the unit module

    # Create units using the module
    king_p1 = unit_manager.create_unit("P1_King", "player1", "King", [0, 0])
    pawn_p1 = unit_manager.create_unit("P1_Pawn1", "player1", "Pawn", [0, 1])
    knight_p2 = unit_manager.create_unit("P2_Knight1", "player2", "Knight", [7, 6])

    print("\nAll active units after creation:")
    for unit in unit_manager.get_all_active_units():
        print(f"- {unit.id} ({unit.unit_type}, Player {unit.player_id}) at {unit.position}, HP: {unit.hp}")

    print("\nKing units:")
    print(f"Player 1 King: {unit_manager.get_king_unit('player1').id}")
    print(f"Player 2 King: {unit_manager.get_king_unit('player2').id}")

    # Simulate some unit updates and damage
    print("\nSimulating unit updates and damage:")
    pawn_p1.receive_damage(5) # Pawn takes damage
    unit_manager.update_units(mock_game) # Update will process damage
    print(f"Pawn P1 HP after update: {pawn_p1.hp}")

    pawn_p1.receive_damage(10) # Pawn is defeated
    unit_manager.update_units(mock_game) # Update will remove defeated unit

    print("\nActive units after pawn defeat:")
    for unit in unit_manager.get_all_active_units():
        print(f"- {unit.id} ({unit.unit_type}, Player {unit.player_id}) at {unit.position}, HP: {unit.hp}")

    # Test an invalid unit type
    invalid_unit = unit_manager.create_unit("Invalid_Unit", "playerX", "Dragon", [4,4])
    print(f"Attempted to create invalid unit: {invalid_unit}")

    print("\n--- End of UnitModule Test ---")
