# real_time_chess/src/utils/constants.py

# This module stores global constants and configurations for the game.
# Using a dedicated constants file helps avoid magic numbers and makes
# it easier to modify game-wide settings.

# --- Game Core Constants ---

# The rate at which the game loop updates, in ticks per second.
# A higher value means more frequent updates and potentially smoother simulation,
# but also higher CPU usage.
GAME_TICK_RATE = 20 # 20 updates per second

# --- Board Dimensions ---

# Default size of the game board (width, height in tiles).
DEFAULT_BOARD_SIZE = (8, 8)

# --- Data File Paths (Relative to the project root or main.py execution) ---
# These paths point to the JSON files where game data is stored.
# Ensure these paths are correct relative to where your main game script runs from.

DATA_DIR = "data/"

UNIT_ARCHETYPES_PATH = DATA_DIR + "unit_archetypes.json"
TERRAIN_TYPES_PATH = DATA_DIR + "terrain_types.json"
CARD_DEFINITIONS_PATH = DATA_DIR + "card_definitions.json"
# Add paths for scenarios, maps, etc., as you create them
# SCENARIOS_DIR = DATA_DIR + "scenarios/"
# MAPS_DIR = DATA_DIR + "maps/"

# --- UI/Display Constants (if using a graphical library like Pygame) ---

# Default screen dimensions for the game window in pixels.
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors (RGB tuples) - example colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GREY = (100, 100, 100)
COLOR_GREEN = (0, 200, 0)
COLOR_RED = (200, 0, 0)
COLOR_BLUE = (0, 0, 200)

# Example Font settings
DEFAULT_FONT_SIZE = 24
# DEFAULT_FONT_PATH = "assets/fonts/game_font.ttf" # Uncomment and specify if you have a font file

# --- Game Phases ---
# Strings representing the different phases of the game.
# These should match the values used in game.py and other modules.
PHASE_OPENING = "Opening"
PHASE_PLANNING = "Planning_Phase" # Detailed sub-phase of Opening
PHASE_BATTLE = "Battle"
PHASE_GAME_OVER = "Game_Over"

# --- Messenger Constants ---
MESSENGER_BASE_HEALTH = 10
MESSENGER_BASE_SPEED = 2 # Tiles per tick
MESSENGER_BASE_RISK_PER_TILE = 0.005 # Base chance per tile to be intercepted

# --- Unit Behavior Types (Examples) ---
BEHAVIOR_MOVEMENT_AGGRESSIVE = "aggressive"
BEHAVIOR_MOVEMENT_DEFENSIVE = "defensive"
BEHAVIOR_MOVEMENT_FLANKING = "flanking"
BEHAVIOR_MOVEMENT_RETREAT = "retreat"

BEHAVIOR_ENGAGEMENT_ENGAGE_ALL = "engage_all"
BEHAVIOR_ENGAGEMENT_TARGET_WEAKEST = "target_weakest"
BEHAVIOR_ENGAGEMENT_TARGET_STRONGEST = "target_strongest"
BEHAVIOR_ENGAGEMENT_TARGET_SPECIFIC_UNIT_TYPE = "target_specific_unit_type"

# Example usage for testing this file directly
if __name__ == "__main__":
    print("--- Testing Constants ---")
    print(f"Game Tick Rate: {GAME_TICK_RATE}")
    print(f"Default Board Size: {DEFAULT_BOARD_SIZE}")
    print(f"Unit Archetypes Path: {UNIT_ARCHETYPES_PATH}")
    print(f"Screen Width: {SCREEN_WIDTH}, Screen Height: {SCREEN_HEIGHT}")
    print(f"Current Game Phase (Example): {PHASE_BATTLE}")
    print(f"Messenger Base Speed: {MESSENGER_BASE_SPEED}")
    print("\n--- End of Constants Test ---")
