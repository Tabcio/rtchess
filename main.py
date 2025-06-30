# real_time_chess/main.py

import sys
import os

# Add the 'src' directory to the Python path so modules can be imported
# This ensures that imports like 'from src.core.game import Game' work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import the main Game class and constants
from src.core.game import Game
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_BOARD_SIZE, GAME_TICK_RATE

def main():
    """
    The main function to initialize and run the game.
    """
    print("Starting Real Time Chess Game...")

    # Initialize the Game instance
    # In a more advanced setup, Game might take parameters for UI, asset loading, etc.
    game = Game()

    # Call the run method of the Game instance to start the game loop
    game.run()

    print("Real Time Chess Game Ended.")

if __name__ == "__main__":
    main()
