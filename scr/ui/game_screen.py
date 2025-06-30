# real_time_chess/src/ui/game_screen.py

import pygame
import os

# Define some basic constants for this example, in a real game these would be in constants.py
TILE_SIZE = 64
BOARD_OFFSET_X = 50
BOARD_OFFSET_Y = 50

# Colors (RGB)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_LIGHT_TILE = (222, 184, 135) # BurlyWood
COLOR_DARK_TILE = (139, 69, 19)   # SaddleBrown
COLOR_FOG_OF_WAR = (50, 50, 50, 200) # Dark grey with transparency
COLOR_KING_AURA = (0, 255, 0, 80) # Green with transparency for King's aura
COLOR_MESSAGE_PATH = (0, 0, 255) # Blue for messenger path
COLOR_PLANNING_LINE = (255, 255, 0) # Yellow for planned moves

# Asset paths (relative to the main.py or where the game is run from)
# This assumes the script is run from the root 'real_time_chess' directory
ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
UNIT_SPRITES_DIR = os.path.join(ASSETS_DIR, 'images', 'units')
TERRAIN_TEXTURES_DIR = os.path.join(ASSETS_DIR, 'images', 'terrain')
UI_ELEMENTS_DIR = os.path.join(ASSETS_DIR, 'images', 'ui')


class GameScreen:
    """
    Renders the main game view using Pygame, including the battlefield, units,
    fog of war, and other visual elements.
    """
    def __init__(self, screen_width: int, screen_height: int, board_size: tuple = (8, 8)):
        """
        Initializes the GameScreen with display dimensions and loads assets.

        Args:
            screen_width (int): The width of the game window/screen in pixels.
            screen_height (int): The height of the game window/screen in pixels.
            board_size (tuple): The (width, height) of the game board in tiles.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.board_size = board_size
        self.tile_size = TILE_SIZE # Calculated dynamically based on constants

        # Initialize Pygame display. pygame.init() is safe to call multiple times.
        pygame.init() 

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("RTChess: The General's Gambit")

        self.assets = {}
        self._load_assets()
        print(f"GameScreen initialized: {screen_width}x{screen_height} pixels. Tile size: {self.tile_size}.")

    def _load_assets(self):
        """Loads all necessary game assets (images, fonts, etc.) or generates placeholders."""
        print("Loading assets or generating placeholders...")
        self.assets['units'] = {}
        self.assets['terrain'] = {}
        self.assets['ui'] = {}

        # Ensure asset directories exist
        os.makedirs(UNIT_SPRITES_DIR, exist_ok=True)
        os.makedirs(TERRAIN_TEXTURES_DIR, exist_ok=True)

        # Unit colors for placeholders
        unit_colors = {"player1": (0, 100, 255), "player2": (255, 0, 0)} # Blue for player1, Red for player2

        # Load unit sprites (example: 'pawn_white.png', 'king_black.png')
        unit_types = ["pawn", "rook", "knight", "bishop", "queen", "king"]
        players = ["player1", "player2"]

        for unit_type in unit_types:
            for player_id in players:
                color_for_unit = unit_colors.get(player_id, (150, 150, 150)) 

                filename = f"{unit_type}_{player_id}.png"
                path = os.path.join(UNIT_SPRITES_DIR, filename)
                try:
                    if os.path.exists(path):
                        image = pygame.image.load(path).convert_alpha()
                        self.assets['units'][f"{unit_type}_{player_id}"] = pygame.transform.scale(image, (self.tile_size, self.tile_size))
                    else:
                        raise FileNotFoundError # Force generation if file doesn't exist
                except (pygame.error, FileNotFoundError) as e:
                    placeholder_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                    placeholder_surface.fill((0,0,0,0)) 
                    pygame.draw.rect(placeholder_surface, color_for_unit, (self.tile_size//4, self.tile_size//4, self.tile_size//2, self.tile_size//2), 0, 5) # Rounded square
                    
                    font = pygame.font.Font(None, 24)
                    text_surface = font.render(unit_type[0].upper(), True, COLOR_WHITE)
                    text_rect = text_surface.get_rect(center=(self.tile_size // 2, self.tile_size // 2))
                    placeholder_surface.blit(text_surface, text_rect)

                    self.assets['units'][f"{unit_type}_{player_id}"] = placeholder_surface
                    print(f"Generated placeholder for unit {unit_type}_{player_id} (Reason: {e})")

        # Terrain colors for placeholders
        terrain_colors = {
            "plains": (144, 238, 144), 
            "forest": (34, 139, 34),   
            "hill": (139, 69, 19)      
        }

        terrain_types = ["plains", "forest", "hill"]
        for terrain_type in terrain_types:
            filename = f"{terrain_type}.png"
            path = os.path.join(TERRAIN_TEXTURES_DIR, filename)
            try:
                if os.path.exists(path):
                    image = pygame.image.load(path).convert()
                    self.assets['terrain'][terrain_type] = pygame.transform.scale(image, (self.tile_size, self.tile_size))
                else:
                    raise FileNotFoundError 
            except (pygame.error, FileNotFoundError) as e:
                placeholder_surface = pygame.Surface((self.tile_size, self.tile_size))
                placeholder_surface.fill(terrain_colors.get(terrain_type, (100, 100, 100))) 
                self.assets['terrain'][terrain_type] = placeholder_surface
                print(f"Generated placeholder for terrain {terrain_type} (Reason: {e})")

        print("Assets loaded or placeholders generated.")


    def draw_board(self, battlefield_module):
        """
        Draws the battlefield grid and terrain textures.
        """
        for y in range(self.board_size[1]):
            for x in range(self.board_size[0]):
                rect = pygame.Rect(
                    BOARD_OFFSET_X + x * self.tile_size,
                    BOARD_OFFSET_Y + y * self.tile_size,
                    self.tile_size,
                    self.tile_size
                )
                color = COLOR_LIGHT_TILE if (x + y) % 2 == 0 else COLOR_DARK_TILE
                pygame.draw.rect(self.screen, color, rect)

                terrain_info = battlefield_module.get_terrain_at([x, y])
                if terrain_info:
                    terrain_type = terrain_info["terrain"].lower()
                    if terrain_type in self.assets['terrain']:
                        self.screen.blit(self.assets['terrain'][terrain_type], rect.topleft)


    def draw_units(self, unit_module, player_id: str, fog_of_war_module):
        """
        Draws active units on the board, respecting the fog of war.
        """
        visible_map = fog_of_war_module.get_visible_area(player_id)
        if not visible_map:
            return

        for unit in unit_module.get_all_active_units():
            x, y = unit.position
            # Always show own units for debug/dev, or if visible through FOW
            is_visible_by_fow = fog_of_war_module.is_within_bounds([x, y]) and visible_map[y][x]
            
            if is_visible_by_fow or unit.player_id == player_id:
                unit_sprite_key = f"{unit.unit_type.lower()}_{unit.player_id}"
                
                if unit_sprite_key in self.assets['units']:
                    unit_image = self.assets['units'][unit_sprite_key]
                    self.screen.blit(unit_image, (BOARD_OFFSET_X + x * self.tile_size, BOARD_OFFSET_Y + y * self.tile_size))
                
                if unit.is_king and unit.player_id == player_id:
                    self.draw_command_aura(unit.position)

    def draw_command_aura(self, king_position):
        """Draws the King's 2-square green command aura."""
        x_c, y_c = king_position
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                ax, ay = x_c + dx, y_c + dy
                if 0 <= ax < self.board_size[0] and 0 <= ay < self.board_size[1]:
                    aura_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                    pygame.draw.rect(aura_surface, COLOR_KING_AURA, aura_surface.get_rect())
                    self.screen.blit(aura_surface, (BOARD_OFFSET_X + ax * self.tile_size, BOARD_OFFSET_Y + ay * self.tile_size))

    def draw_messengers(self, messenger_module, player_id: str, fog_of_war_module):
        """
        Draws messengers and their paths.
        """
        visible_map = fog_of_war_module.get_visible_area(player_id)
        if not visible_map:
            return

        for messenger in messenger_module.get_all_active_messengers():
            mx, my = messenger.position
            target_unit = messenger.target_unit 
            
            is_messenger_visible = fog_of_war_module.is_within_bounds([mx, my]) and visible_map[my][mx]
            is_target_visible = False
            if target_unit:
                tx, ty = target_unit.position
                is_target_visible = fog_of_war_module.is_within_bounds([tx, ty]) and visible_map[ty][tx]

            if is_messenger_visible:
                center_x = BOARD_OFFSET_X + mx * self.tile_size + self.tile_size // 2
                center_y = BOARD_OFFSET_Y + my * self.tile_size + self.tile_size // 2
                pygame.draw.circle(self.screen, COLOR_MESSAGE_PATH, (center_x, center_y), self.tile_size // 6)

                if is_target_visible:
                    target_center_x = BOARD_OFFSET_X + tx * self.tile_size + self.tile_size // 2
                    target_center_y = BOARD_OFFSET_Y + ty * self.tile_size + self.tile_size // 2
                    pygame.draw.line(self.screen, COLOR_MESSAGE_PATH, (center_x, center_y), (target_center_x, target_center_y), 2)


    def draw_planning_lines(self, planning_data):
        """
        Draws planned movement lines during the planning phase.
        """
        for start_pos, end_pos in planning_data:
            start_pixel_x = BOARD_OFFSET_X + start_pos[0] * self.tile_size + self.tile_size // 2
            start_pixel_y = BOARD_OFFSET_Y + start_pos[1] * self.tile_size + self.tile_size // 2
            end_pixel_x = BOARD_OFFSET_X + end_pos[0] * self.tile_size + self.tile_size // 2
            end_pixel_y = BOARD_OFFSET_Y + end_pos[1] * self.tile_size + self.tile_size // 2
            pygame.draw.line(self.screen, COLOR_PLANNING_LINE, (start_pixel_x, start_pixel_y), (end_pixel_x, end_pixel_y), 3)


    def draw_fog_of_war(self, fog_of_war_module, player_id: str):
        """
        Applies the fog of war overlay. This should be drawn *on top* of other elements.
        """
        visible_map = fog_of_war_module.get_visible_area(player_id)
        if not visible_map:
            return

        fog_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for y in range(self.board_size[1]):
            for x in range(self.board_size[0]):
                if not visible_map[y][x]:
                    rect = pygame.Rect(
                        BOARD_OFFSET_X + x * self.tile_size,
                        BOARD_OFFSET_Y + y * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    )
                    pygame.draw.rect(fog_surface, COLOR_FOG_OF_WAR, rect)
        self.screen.blit(fog_surface, (0, 0))


    def render(self, game_state, player_id: str, planning_data=None):
        """
        Renders the entire game screen for a specific player's perspective.
        """
        self.screen.fill(COLOR_BLACK) # Clear the screen each frame

        self.draw_board(game_state.battlefield_module)
        self.draw_units(game_state.unit_module, player_id, game_state.fog_of_war_module)
        self.draw_messengers(game_state.messenger_module, player_id, game_state.fog_of_war_module)

        if planning_data:
            self.draw_planning_lines(planning_data)

        self.draw_fog_of_war(game_state.fog_of_war_module, player_id)

        # TODO: Add drawing for UI elements (HUD, cards etc.) from hud.py if implemented

        pygame.display.flip() # Update the full display Surface to the screen
