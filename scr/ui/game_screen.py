# real_time_chess/src/ui/game_screen.py

# This module will be responsible for drawing the game state to the screen.
# It assumes a graphical library (like Pygame or a simple console drawing) will be used.
# For this skeletal version, we'll use print statements to simulate drawing.

# Import necessary modules (assuming a mock game state for testing)
# In a real UI, you'd import specific UI components or assets.

class GameScreen:
    """
    Renders the main game view, including the battlefield, units, and fog of war.
    This class acts as the visual representation layer of the game state.
    """
    def __init__(self, screen_width: int, screen_height: int, board_size: tuple = (8, 8)):
        """
        Initializes the GameScreen with display dimensions.

        Args:
            screen_width (int): The width of the game window/screen in pixels.
            screen_height (int): The height of the game window/screen in pixels.
            board_size (tuple): The (width, height) of the game board in tiles.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.board_size = board_size
        self.tile_size = min(screen_width // board_size[0], screen_height // board_size[1]) # Calculate tile size
        print(f"GameScreen initialized: {screen_width}x{screen_height} pixels. Tile size: {self.tile_size}.")

    def draw_board(self, battlefield_module):
        """
        Draws the battlefield grid and terrain.

        Args:
            battlefield_module: Reference to the BattlefieldModule for terrain data.
        """
        print("\n--- Drawing Battlefield ---")
        for y in range(self.board_size[1]):
            row_str = ""
            for x in range(self.board_size[0]):
                terrain_info = battlefield_module.get_terrain_at([x, y])
                if terrain_info:
                    terrain_char = terrain_info["terrain"][0].upper() # 'P' for Plains, 'F' for Forest, 'H' for Hill
                    row_str += f"{terrain_char} "
                else:
                    row_str += "? " # Unknown terrain
            print(row_str)
        print("---------------------------")

    def draw_units(self, unit_module, player_id: str, fog_of_war_module):
        """
        Draws active units on the board, respecting the fog of war.

        Args:
            unit_module: Reference to the UnitModule for unit data.
            player_id (str): The ID of the player whose view is being rendered.
            fog_of_war_module: Reference to the FogOfWarModule for visibility data.
        """
        print(f"\n--- Drawing Units for Player '{player_id}' ---")
        visible_map = fog_of_war_module.get_visible_area(player_id)
        if not visible_map:
            print("  Player map not initialized. Cannot draw units.")
            return

        # Create a temporary board representation to draw units on
        display_grid = [['. ' for _ in range(self.board_size[0])] for _ in range(self.board_size[1])]

        for unit in unit_module.get_all_active_units():
            x, y = unit.position
            # Only draw unit if its position is visible to the player
            if fog_of_war_module.is_within_bounds([x, y]) and visible_map[y][x]:
                if unit.is_king:
                    display_grid[y][x] = f"K{unit.player_id[-1]} " # K1 or K2
                elif unit.player_id == player_id:
                    display_grid[y][x] = f"{unit.unit_type[0].upper()}{unit.player_id[-1]} " # P1, R1, N2 etc.
                else: # Enemy unit
                    display_grid[y][x] = "E " # Simple 'E' for enemy, regardless of type
            # TODO: Add logic to draw based on last_seen_unit_id if using that FOW feature

        for y in range(self.board_size[1]):
            row_str = ""
            for x in range(self.board_size[0]):
                if not visible_map[y][x]:
                    row_str += "XX" # Fog of war
                else:
                    row_str += display_grid[y][x]
            print(row_str)
        print("-------------------------")

    def draw_fog_of_war(self, fog_of_war_module, player_id: str):
        """
        Displays the fog of war overlay for a given player.
        (This is partially handled by draw_units, but can be separate for pure FOW view).

        Args:
            fog_of_war_module: Reference to the FogOfWarModule.
            player_id (str): The ID of the player.
        """
        fog_of_war_module.display_player_map(player_id) # Uses the FOW module's own display method

    def render(self, game_state, player_id: str):
        """
        Renders the entire game screen for a specific player's perspective.

        Args:
            game_state: A reference to the main Game object.
            player_id (str): The ID of the player whose view is being rendered.
        """
        print(f"\n=============== Rendering for Player '{player_id}' ===============\n")
        self.draw_board(game_state.battlefield_module)
        self.draw_units(game_state.unit_module, player_id, game_state.fog_of_war_module)
        # self.draw_fog_of_war(game_state.fog_of_war_module, player_id) # Can be called separately if desired
        # TODO: Add drawing for messengers, UI elements (HUD, cards etc.)
        print("\n=======================================================\n")


# Example usage for testing this file directly
if __name__ == "__main__":
    print("--- Testing GameScreen ---")

    # Mock dependent modules and classes for standalone testing
    class MockUnit:
        def __init__(self, unit_id, player_id, pos, unit_type, is_king=False):
            self.id = unit_id
            self.player_id = player_id
            self.position = list(pos)
            self.unit_type = unit_type
            self.is_king = is_king
            self.is_alive = True # Assume alive for drawing

    class MockUnitModule:
        def __init__(self):
            self.units = {
                "P1_King": MockUnit("P1_King", "player1", [0, 0], "King", True),
                "P1_Pawn1": MockUnit("P1_Pawn1", "player1", [1, 1], "Pawn"),
                "P1_Rook1": MockUnit("P1_Rook1", "player1", [0, 7], "Rook"),
                "P2_King": MockUnit("P2_King", "player2", [7, 7], "King", True),
                "P2_Pawn1": MockUnit("P2_Pawn1", "player2", [6, 6], "Pawn"),
                "P2_Knight1": MockUnit("P2_Knight1", "player2", [5, 5], "Knight"),
            }
        def get_all_active_units(self):
            return list(self.units.values())

    class MockBattlefieldModule:
        def __init__(self, size=(8, 8)):
            self.size = size
            self.grid = [[{"terrain": "Plains"} for _ in range(size[0])] for _ in range(size[1])]
            self.grid[2][2]["terrain"] = "Forest"
            self.grid[3][3]["terrain"] = "Hill"

        def get_terrain_at(self, position):
            x, y = position
            if 0 <= x < self.size[0] and 0 <= y < self.size[1]:
                terrain_type = self.grid[y][x]["terrain"]
                # Simulating TERRAIN_TYPES dict for testing
                mock_terrain_types = {
                    "Plains": {"terrain": "Plains"}, "Forest": {"terrain": "Forest"}, "Hill": {"terrain": "Hill"}
                }
                return mock_terrain_types.get(terrain_type)
            return None
        def is_within_bounds(self, pos):
            x, y = pos
            return 0 <= x < self.size[0] and 0 <= y < self.size[1]


    class MockFogOfWarModule:
        def __init__(self, board_size=(8,8)):
            self.board_size = board_size
            self.player_maps = {} # {player_id: [[bool]]}

        def initialize_player_map(self, player_id):
            self.player_maps[player_id] = [[False for _ in range(self.board_size[0])] for _ in range(self.board_size[1])]

        def reveal_area(self, player_id, center_pos, radius):
            x_c, y_c = center_pos
            for y in range(max(0, y_c - radius), min(self.board_size[1], y_c + radius + 1)):
                for x in range(max(0, x_c - radius), min(self.board_size[0], x_c + radius + 1)):
                    distance = ((x - x_c)**2 + (y - y_c)**2)**0.5
                    if distance <= radius:
                        if self.is_within_bounds([x, y]): # Ensure it's within bounds before setting
                             self.player_maps[player_id][y][x] = True

        def get_visible_area(self, player_id):
            return self.player_maps.get(player_id, [])

        def display_player_map(self, player_id):
            # Already implemented in FogOfWarModule, just a mock here
            print(f"  (Displaying player '{player_id}' raw FOW map via mock)")
            player_map = self.player_maps.get(player_id, [])
            for row in player_map:
                print(" ".join(['O' if cell else 'X' for cell in row]))

        def is_within_bounds(self, pos):
            x, y = pos
            return 0 <= x < self.board_size[0] and 0 <= y < self.board_size[1]


    # A minimal MockGame to hold references to the modules
    class MockGame:
        def __init__(self, board_size=(8,8)):
            self.unit_module = MockUnitModule()
            self.battlefield_module = MockBattlefieldModule(board_size)
            self.fog_of_war_module = MockFogOfWarModule(board_size)
            # Initialize player maps and reveal King's starting area
            self.fog_of_war_module.initialize_player_map("player1")
            self.fog_of_war_module.initialize_player_map("player2")

            # Reveal initial King areas for testing
            p1_king_pos = self.unit_module.units["P1_King"].position
            p1_king_sight = self.unit_module.units["P1_King"].sight_range if hasattr(self.unit_module.units["P1_King"], 'sight_range') else 3
            self.fog_of_war_module.reveal_area("player1", p1_king_pos, p1_king_sight)

            p2_king_pos = self.unit_module.units["P2_King"].position
            p2_king_sight = self.unit_module.units["P2_King"].sight_range if hasattr(self.unit_module.units["P2_King"], 'sight_range') else 3
            self.fog_of_war_module.reveal_area("player2", p2_king_pos, p2_king_sight)


    game_board_size = (8, 8)
    mock_game_instance = MockGame(game_board_size)
    game_screen = GameScreen(screen_width=800, screen_height=600, board_size=game_board_size)

    # Render for Player 1
    game_screen.render(mock_game_instance, "player1")

    # Render for Player 2
    game_screen.render(mock_game_instance, "player2")

    # Simulate P1_Pawn1 moving and revealing more, then re-render
    print("\n--- Simulating P1_Pawn1 move and re-rendering for Player 1 ---")
    mock_game_instance.unit_module.units["P1_Pawn1"].position = [3, 2]
    # Update FOW based on new pawn position (simulate a game tick's FOW update)
    mock_game_instance.fog_of_war_module.update_player_map_from_unit_vision(
        "player1", mock_game_instance.unit_module.units["P1_Pawn1"], mock_game_instance.battlefield_module
    )
    game_screen.render(mock_game_instance, "player1")

    print("\n--- End of GameScreen Test ---")
