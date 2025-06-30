# real_time_chess/src/ui/hud.py

# This module will be responsible for displaying the Heads-Up Display (HUD)
# to the player, including player stats, a minimap, and other vital information.
# For this skeletal version, we'll use print statements to simulate UI elements.

class HUD:
    """
    Renders the Heads-Up Display for the player, providing immediate access
    to critical game information.
    """
    def __init__(self, screen_width: int, screen_height: int):
        """
        Initializes the HUD with display dimensions.

        Args:
            screen_width (int): The width of the game window/screen in pixels.
            screen_height (int): The height of the game window/screen in pixels.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        print(f"HUD initialized: {screen_width}x{screen_height} pixels.")

    def _draw_player_stats(self, player_id: str, game_state):
        """
        Displays core player statistics.

        Args:
            player_id (str): The ID of the player whose stats are displayed.
            game_state: A reference to the main Game object.
        """
        print(f"\n--- Player '{player_id}' Stats ---")
        player_king = game_state.unit_module.get_king_unit(player_id)
        if player_king:
            print(f"  King HP: {player_king.hp}/{player_king.max_hp}")
            print(f"  King Position: {player_king.position}")
        else:
            print("  King status: Not Found or Defeated")

        player_units = game_state.unit_module.get_units_by_player(player_id)
        print(f"  Active Units: {len(player_units)}")

        player_hand = game_state.card_system_module.player_hands.get(player_id, [])
        print(f"  Cards in Hand: {len(player_hand)}")
        if player_hand:
            print(f"    Cards: {', '.join([game_state.card_system_module.card_definitions.get(c, {}).get('name', c) for c in player_hand])}")
        # TODO: Add resources, score, etc.
        print("----------------------------")

    def _draw_minimap(self, player_id: str, game_state):
        """
        Displays a simplified minimap showing visible areas and key unit locations.

        Args:
            player_id (str): The ID of the player whose minimap is displayed.
            game_state: A reference to the main Game object.
        """
        print(f"\n--- Player '{player_id}' Minimap ---")
        visible_map = game_state.fog_of_war_module.get_visible_area(player_id)
        board_size = game_state.battlefield_module.size

        if not visible_map:
            print("  Minimap not available (FOW not initialized).")
            return

        minimap_grid = [['.' for _ in range(board_size[0])] for _ in range(board_size[1])]

        # Mark visible areas
        for y in range(board_size[1]):
            for x in range(board_size[0]):
                if visible_map[y][x]:
                    minimap_grid[y][x] = 'O' # 'O' for visible

        # Mark player's king
        player_king = game_state.unit_module.get_king_unit(player_id)
        if player_king and player_king.is_alive and game_state.fog_of_war_module.is_within_bounds(player_king.position):
            kx, ky = player_king.position
            minimap_grid[ky][kx] = 'K' # 'K' for King

        # Mark known enemy units (simplified for now - always visible on map if FOW allows)
        for unit in game_state.unit_module.get_all_active_units():
            if unit.player_id != player_id and game_state.fog_of_war_module.is_within_bounds(unit.position):
                ux, uy = unit.position
                # Only show if unit's position is currently visible to the player
                if visible_map[uy][ux]:
                    minimap_grid[uy][ux] = 'E' # 'E' for Enemy

        for row in minimap_grid:
            print(" ".join(row))
        print("--------------------------")

    def _draw_game_info(self, game_state):
        """
        Displays general game information.

        Args:
            game_state: A reference to the main Game object.
        """
        print("\n--- Game Info ---")
        print(f"  Current Phase: {game_state.current_phase}")
        print(f"  Game Tick: {game_state.tick_count}")
        # TODO: Add time elapsed, objective status, etc.
        print("-----------------")

    def render(self, game_state, player_id: str):
        """
        Renders the full HUD for a specific player's perspective.

        Args:
            game_state: A reference to the main Game object.
            player_id (str): The ID of the player whose HUD is being rendered.
        """
        print(f"\n============== HUD for Player '{player_id}' ==============\n")
        self._draw_player_stats(player_id, game_state)
        self._draw_minimap(player_id, game_state)
        self._draw_game_info(game_state)
        print("\n=======================================================\n")


# Example usage for testing this file directly
if __name__ == "__main__":
    print("--- Testing HUD ---")

    # Mock dependent modules and classes for standalone testing
    class MockUnit:
        def __init__(self, unit_id, player_id, pos, hp, max_hp, unit_type, is_king=False):
            self.id = unit_id
            self.player_id = player_id
            self.position = list(pos)
            self.hp = hp
            self.max_hp = max_hp
            self.unit_type = unit_type
            self.is_king = is_king
            self.is_alive = True
            if is_king: self.hq_visual_range = 3 # For King's initial FOW

    class MockUnitModule:
        def __init__(self):
            self.units = {
                "P1_King": MockUnit("P1_King", "player1", [0, 0], 50, 50, "King", True),
                "P1_Pawn1": MockUnit("P1_Pawn1", "player1", [1, 1], 10, 10, "Pawn"),
                "P2_King": MockUnit("P2_King", "player2", [7, 7], 50, 50, "King", True),
                "P2_Pawn1": MockUnit("P2_Pawn1", "player2", [6, 6], 10, 10, "Pawn"),
                "P2_Rook1": MockUnit("P2_Rook1", "player2", [4, 4], 30, 30, "Rook"), # Enemy unit potentially visible
            }
        def get_king_unit(self, player_id):
            return next((u for u in self.units.values() if u.player_id == player_id and u.is_king), None)
        def get_units_by_player(self, player_id):
            return [u for u in self.units.values() if u.player_id == player_id and u.is_alive]
        def get_all_active_units(self):
            return [u for u in self.units.values() if u.is_alive]

    class MockFogOfWarModule:
        def __init__(self, board_size=(8,8)):
            self.board_size = board_size
            self.player_maps = {"player1": [[False for _ in range(board_size[0])] for _ in range(board_size[1])],
                                "player2": [[False for _ in range(board_size[0])] for _ in range(board_size[1])]}
        def get_visible_area(self, player_id):
            return self.player_maps.get(player_id, [])
        def reveal_area(self, player_id, center_pos, radius):
            x_c, y_c = center_pos
            for y in range(max(0, y_c - radius), min(self.board_size[1], y_c + radius + 1)):
                for x in range(max(0, x_c - radius), min(self.board_size[0], x_c + radius + 1)):
                    distance = ((x - x_c)**2 + (y - y_c)**2)**0.5
                    if distance <= radius:
                        if self.is_within_bounds([x, y]):
                             self.player_maps[player_id][y][x] = True
        def is_within_bounds(self, pos):
            x, y = pos
            return 0 <= x < self.board_size[0] and 0 <= y < self.board_size[1]


    class MockCardSystemModule:
        def __init__(self):
            self.player_hands = {
                "player1": ["morale_boost", "rapid_dispatch"],
                "player2": ["scouting_report"]
            }
            self.card_definitions = {
                "morale_boost": {"name": "Morale Boost"},
                "rapid_dispatch": {"name": "Rapid Dispatch"},
                "scouting_report": {"name": "Scouting Report"}
            }

    class MockBattlefieldModule:
        def __init__(self, size=(8,8)):
            self.size = size
        # Add a placeholder for get_terrain_at if needed by minimap for terrain rendering
        def get_terrain_at(self, pos):
            return {"terrain": "Plains"}

    class MockGame:
        def __init__(self, board_size=(8,8)):
            self.unit_module = MockUnitModule()
            self.fog_of_war_module = MockFogOfWarModule(board_size)
            self.card_system_module = MockCardSystemModule()
            self.battlefield_module = MockBattlefieldModule(board_size) # For minimap grid size
            self.current_phase = "Battle"
            self.tick_count = 123 # Example tick count

            # Initialize FOW for players based on King's starting sight
            p1_king = self.unit_module.get_king_unit("player1")
            if p1_king:
                self.fog_of_war_module.reveal_area("player1", p1_king.position, p1_king.hq_visual_range)
            p2_king = self.unit_module.get_king_unit("player2")
            if p2_king:
                self.fog_of_war_module.reveal_area("player2", p2_king.position, p2_king.hq_visual_range)

            # Make P2_Rook1 visible to P1 for minimap enemy display
            # Simulate P1_Pawn1 seeing P2_Rook1
            p1_pawn1 = self.unit_module.get_units_by_player("player1")[0] # Get P1_Pawn1
            if p1_pawn1:
                # Move pawn so it sees rook
                p1_pawn1.position = [4,3] # Adjust pawn position to be near rook [4,4]
                # Simulate the FOW update from this unit
                self.fog_of_war_module.reveal_area("player1", p1_pawn1.position, p1_pawn1.sight_range)


    mock_game_instance = MockGame(board_size=(8, 8))
    hud = HUD(screen_width=800, screen_height=600)

    # Render HUD for Player 1
    hud.render(mock_game_instance, "player1")

    # Render HUD for Player 2
    hud.render(mock_game_instance, "player2")

    print("\n--- End of HUD Test ---")
