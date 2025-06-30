# real_time_chess/src/modules/fog_of_war_module.py

class FogOfWarModule:
    """
    Manages the fog of war and visibility for each player on the battlefield.
    Each player has their own view of the map, which is revealed by their units' sight
    ranges and messenger reports.
    """
    def __init__(self, board_size: tuple = (8, 8)):
        """
        Initializes the FogOfWarModule with the battlefield dimensions.

        Args:
            board_size (tuple): A tuple (width, height) representing the dimensions of the board.
        """
        self.board_size = board_size
        # Stores player-specific knowledge of the map:
        # {player_id: [[is_visible_boolean, last_seen_unit_id_or_None, last_seen_terrain_type_or_None]]}
        # For a skeletal version, we'll start with just is_visible_boolean.
        self.player_maps = {}
        print(f"FogOfWarModule initialized for board size {board_size[0]}x{board_size[1]}.")

    def initialize_player_map(self, player_id: str):
        """
        Sets up the initial fog of war for a specific player.
        All tiles are initially unseen (False).

        Args:
            player_id (str): The ID of the player to initialize the map for.
        """
        # Create a grid where all tiles are initially hidden (False)
        self.player_maps[player_id] = [[False for _ in range(self.board_size[0])] for _ in range(self.board_size[1])]
        print(f"Initial fog of war set for player '{player_id}'.")

    def reveal_area(self, player_id: str, center_pos: list, radius: int):
        """
        Reveals a circular area around a given position for a specific player.
        This simulates visibility from a unit or headquarters.

        Args:
            player_id (str): The ID of the player whose map is being updated.
            center_pos (list): The [x, y] coordinates of the center of the revealed area.
            radius (int): The radius of the circular area to reveal.
        """
        if player_id not in self.player_maps:
            print(f"Warning: Player '{player_id}' map not initialized. Cannot reveal area.")
            return

        x_c, y_c = center_pos
        revealed_count = 0
        for y in range(max(0, y_c - radius), min(self.board_size[1], y_c + radius + 1)):
            for x in range(max(0, x_c - radius), min(self.board_size[0], x_c + radius + 1)):
                # Calculate distance to determine if within circular radius
                distance = ((x - x_c)**2 + (y - y_c)**2)**0.5
                if distance <= radius:
                    if not self.player_maps[player_id][y][x]: # Only update if not already visible
                        self.player_maps[player_id][y][x] = True
                        revealed_count += 1
                        # TODO: In a more advanced version, also update 'last_seen_unit_id' and 'last_seen_terrain_type'
                        # based on what's actually at (x,y) from the battlefield state.
        # print(f"Player '{player_id}' revealed {revealed_count} new tiles around {center_pos} (radius {radius}).")

    def update_player_map_from_unit_vision(self, player_id, unit, battlefield_module):
        """
        Updates a player's map based on the current visibility of a specific unit.
        Units constantly reveal the area around them.

        Args:
            player_id (str): The ID of the player whose map is being updated.
            unit: The Unit object whose vision is to be applied.
            battlefield_module: Reference to the BattlefieldModule for board boundaries.
        """
        if not unit.is_alive or unit.sight_range <= 0:
            return

        # Reveal area around the unit's current position
        self.reveal_area(player_id, unit.position, unit.sight_range)

        # TODO: Add logic here to identify and mark enemy units/terrain features within the unit's sight range
        # on the player's map data structure (e.g., self.player_maps[player_id][y][x] = [True, enemy_unit_id, terrain_type]).

    def update_player_map_from_report(self, player_id: str, report_data: dict):
        """
        Updates a player's map based on information received from a messenger report.
        Reports can contain visibility updates, unit statuses, and enemy sightings.

        Args:
            player_id (str): The ID of the player whose map is being updated.
            report_data (dict): The data payload from the messenger, containing visibility info.
        """
        if player_id not in self.player_maps:
            print(f"Warning: Player '{player_id}' map not initialized. Cannot process report.")
            return

        visibility_updates = report_data.get("visibility_update", [])
        updated_tiles_count = 0
        for x, y, is_visible in visibility_updates:
            if 0 <= y < self.board_size[1] and 0 <= x < self.board_size[0]:
                if not self.player_maps[player_id][y][x] and is_visible:
                    self.player_maps[player_id][y][x] = True
                    updated_tiles_count += 1
        # if updated_tiles_count > 0:
            # print(f"Player '{player_id}' map updated with {updated_tiles_count} new visible tiles from report.")

        # TODO: Process other parts of the report_data (e.g., enemy sightings, unit statuses)
        # and update corresponding information in self.player_maps or a separate 'known_enemy_positions' data structure.

    def get_visible_area(self, player_id: str) -> list[list[bool]]:
        """
        Returns the current visibility grid for a specific player.

        Args:
            player_id (str): The ID of the player.

        Returns:
            list[list[bool]]: A 2D list where True indicates a visible tile, False otherwise.
                              Returns an empty list if player map is not initialized.
        """
        return self.player_maps.get(player_id, [])

    def display_player_map(self, player_id: str):
        """
        Prints a simple textual representation of a player's visible map.
        'O' for visible, 'X' for fog of war.
        """
        if player_id not in self.player_maps:
            print(f"Cannot display map: Player '{player_id}' map not initialized.")
            return

        print(f"\n--- Player '{player_id}' Map View ---")
        player_map = self.player_maps[player_id]
        for row in player_map:
            print(" ".join(['O' if cell else 'X' for cell in row]))
        print("--------------------------")


# Example usage for testing this file directly
if __name__ == "__main__":
    print("--- Testing FogOfWarModule ---")

    # Mock dependent classes for standalone testing
    class MockUnit:
        def __init__(self, unit_id, player_id, pos, sight_range, is_alive=True):
            self.id = unit_id
            self.player_id = player_id
            self.position = list(pos)
            self.sight_range = sight_range
            self.is_alive = is_alive

    class MockBattlefieldModule:
        def __init__(self, size=(8, 8)):
            self.size = size
        def is_within_bounds(self, pos):
            x, y = pos
            return 0 <= x < self.size[0] and 0 <= y < self.size[1]
        def get_terrain_at(self, pos):
            return {"terrain": "Plains"} # Simplified mock

    board_size = (8, 8)
    fog_manager = FogOfWarModule(board_size=board_size)
    mock_battlefield = MockBattlefieldModule(size=board_size)

    player1_id = "player1"
    player2_id = "player2"

    fog_manager.initialize_player_map(player1_id)
    fog_manager.initialize_player_map(player2_id)

    # Display initial fogged map
    fog_manager.display_player_map(player1_id)

    # Simulate King's initial vision
    king1_pos = [0, 0]
    king1_sight = 3 # King's sight range
    mock_king1 = MockUnit("K1", player1_id, king1_pos, king1_sight)

    print(f"\nRevealing area around King 1 at {king1_pos} with sight {king1_sight}:")
    fog_manager.reveal_area(player1_id, king1_pos, king1_sight)
    fog_manager.display_player_map(player1_id)

    # Simulate a unit moving and revealing more
    pawn1_pos = [4, 4]
    pawn1_sight = 2
    mock_pawn1 = MockUnit("P1", player1_id, pawn1_pos, pawn1_sight)

    print(f"\nUpdating Player 1 map from Pawn 1 at {pawn1_pos} with sight {pawn1_sight}:")
    fog_manager.update_player_map_from_unit_vision(player1_id, mock_pawn1, mock_battlefield)
    fog_manager.display_player_map(player1_id)

    # Simulate an enemy unit that Player 2's unit sees
    enemy_unit_pos = [2, 2] # This unit is visible to P1's pawn, but mock only tracks visibility, not enemy entities
    mock_enemy_unit = MockUnit("E1", player2_id, enemy_unit_pos, 0)

    # Simulate a report from a unit
    print("\nSimulating a report with visibility update for Player 2:")
    report_from_p2_unit = {
        "unit_id": "P2_Scout",
        "position": [5, 5],
        "visibility_update": [
            [5, 5, True], [4, 5, True], [6, 5, True],
            [5, 4, True], [5, 6, True]
        ]
    }
    fog_manager.update_player_map_from_report(player2_id, report_from_p2_unit)
    fog_manager.display_player_map(player2_id)

    print("\n--- End of FogOfWarModule Test ---")
