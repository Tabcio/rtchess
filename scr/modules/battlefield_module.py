# real_time_chess/src/modules/battlefield_module.py

# You would ideally load TERRAIN_TYPES from data/terrain_types.json
# For now, it's defined here as a placeholder for self-containment.
TERRAIN_TYPES = {
    "Plains": {"movement_modifier": 1.0, "visibility_modifier": 1.0, "combat_modifier": 1.0},
    "Forest": {"movement_modifier": 0.7, "visibility_modifier": 0.8, "combat_modifier": 1.1}, # Provides cover
    "Hill": {"movement_modifier": 0.9, "visibility_modifier": 1.2, "combat_modifier": 1.05}, # Higher ground
}

class BattlefieldModule:
    """
    Manages the game board, including its dimensions, terrain types, and the
    current positions of all units on the grid.
    """
    def __init__(self, size: tuple = (8, 8)):
        """
        Initializes the battlefield grid.

        Args:
            size (tuple): A tuple (width, height) representing the dimensions of the board.
        """
        self.size = size # (width, height)
        # The grid stores information about each tile, e.g., terrain type, obstacles
        # Each element is a dictionary to allow for easy expansion (e.g., {'terrain': 'Forest', 'has_obstacle': True})
        self.grid = [[{"terrain": "Plains"} for _ in range(size[0])] for _ in range(size[1])]

        # A quick lookup for unit positions: {unit_id: [x, y]}
        # This is kept separate from the grid itself for efficiency in unit movement/lookup
        self.unit_positions_map = {} # {unit_id: [x, y]}

        print(f"Battlefield initialized with size: {self.size[0]}x{self.size[1]}.")

    def get_terrain_at(self, position: list) -> dict:
        """
        Retrieves the terrain information for a given grid position.

        Args:
            position (list): The [x, y] coordinates on the board.

        Returns:
            dict: A dictionary containing the terrain type and its modifiers, or None if out of bounds.
        """
        x, y = position
        if self.is_within_bounds(position):
            terrain_type = self.grid[y][x]["terrain"]
            return TERRAIN_TYPES.get(terrain_type)
        return None # Position is out of bounds

    def is_within_bounds(self, position: list) -> bool:
        """
        Checks if a given position is within the boundaries of the battlefield grid.

        Args:
            position (list): The [x, y] coordinates to check.

        Returns:
            bool: True if the position is within bounds, False otherwise.
        """
        x, y = position
        return 0 <= x < self.size[0] and 0 <= y < self.size[1]

    def update_unit_position(self, unit_id: str, new_position: list):
        """
        Updates a unit's position internally.
        This method is called by units when they move.

        Args:
            unit_id (str): The ID of the unit whose position is being updated.
            new_position (list): The new [x, y] coordinates of the unit.
        """
        if self.is_within_bounds(new_position):
            self.unit_positions_map[unit_id] = list(new_position)
            # print(f"Unit {unit_id} moved to {new_position}.")
        else:
            print(f"Warning: Unit {unit_id} attempted to move out of bounds to {new_position}.")
            # TODO: Handle units moving out of bounds (e.g., stopping them, error)

    def get_unit_position(self, unit_id: str) -> list:
        """
        Retrieves the current position of a specific unit.

        Args:
            unit_id (str): The ID of the unit.

        Returns:
            list: The [x, y] coordinates of the unit, or None if the unit is not found.
        """
        return self.unit_positions_map.get(unit_id)

    def add_obstacle(self, position: list, obstacle_type: str = "impassable"):
        """
        Adds an obstacle to a specific grid position.
        This is a placeholder for future terrain expansion.

        Args:
            position (list): The [x, y] coordinates to add the obstacle.
            obstacle_type (str): The type of obstacle (e.g., "impassable", "slow").
        """
        x, y = position
        if self.is_within_bounds(position):
            self.grid[y][x]["obstacle"] = obstacle_type
            print(f"Added '{obstacle_type}' obstacle at {position}.")
        else:
            print(f"Cannot add obstacle: {position} is out of bounds.")

    def set_terrain(self, position: list, terrain_type: str):
        """
        Sets the terrain type for a specific grid position.

        Args:
            position (list): The [x, y] coordinates to set the terrain.
            terrain_type (str): The name of the terrain type (e.g., "Forest", "Hill").
        """
        x, y = position
        if self.is_within_bounds(position) and terrain_type in TERRAIN_TYPES:
            self.grid[y][x]["terrain"] = terrain_type
            print(f"Set terrain at {position} to {terrain_type}.")
        else:
            print(f"Cannot set terrain: {position} out of bounds or '{terrain_type}' is an unknown type.")


# Example usage for testing this file directly
if __name__ == "__main__":
    print("--- Testing BattlefieldModule ---")

    board = BattlefieldModule(size=(10, 10))

    print("\nChecking terrain at (1, 1):", board.get_terrain_at([1, 1]))
    print("Checking terrain at (10, 10) (out of bounds):", board.get_terrain_at([10, 10]))

    print("\nSetting terrain at (2, 2) to Forest:")
    board.set_terrain([2, 2], "Forest")
    print("Terrain at (2, 2) now:", board.get_terrain_at([2, 2]))

    print("\nAdding an obstacle at (5, 5):")
    board.add_obstacle([5, 5])
    print("Grid info at (5, 5):", board.grid[5][5])

    print("\nUpdating unit positions:")
    board.update_unit_position("P1_King", [0, 0])
    board.update_unit_position("P1_Pawn1", [1, 1])
    board.update_unit_position("P2_Knight1", [7, 8])

    print(f"Position of P1_King: {board.get_unit_position('P1_King')}")
    print(f"Position of P2_Knight1: {board.get_unit_position('P2_Knight1')}")
    print(f"Position of non-existent unit: {board.get_unit_position('NonExistentUnit')}")

    print("\nSimulating unit movement and position update:")
    # In a real game, units call battlefield_module.update_unit_position
    # This mock directly updates via the module
    board.update_unit_position("P1_Pawn1", [1, 2])
    print(f"New position of P1_Pawn1: {board.get_unit_position('P1_Pawn1')}")

    print("\n--- End of BattlefieldModule Test ---")
