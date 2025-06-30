import time
import random

# Import necessary modules from the defined file structure
from ..modules.unit_module import UnitModule
from ..modules.battlefield_module import BattlefieldModule
from ..modules.combat_module import CombatModule
from ..modules.fog_of_war_module import FogOfWarModule
from ..modules.messenger_module import MessengerModule
from ..modules.card_system_module import CardSystemModule

# You would ideally import this from src.utils.constants
# For now, defining it here for self-containment of this file.
GAME_TICK_RATE = 20 # Updates per second


class Game:
    """Manages the overall game state, phases, and interactions between modules."""
    def __init__(self):
        self.current_phase = "Opening" # "Opening", "Battle", "Game_Over"
        self.players = ["player1", "player2"] # Example players
        self.game_running = False
        self.tick_count = 0

        # Initialize core modules
        # These will eventually be instantiated in main.py and passed to Game
        # For now, we instantiate them here directly for a self-contained example.
        self.unit_module = UnitModule()
        self.battlefield_module = BattlefieldModule()
        self.combat_module = CombatModule()
        self.fog_of_war_module = FogOfWarModule(self.battlefield_module.size)
        self.messenger_module = MessengerModule()
        self.card_system_module = CardSystemModule()

    def initialize_game(self):
        """Sets up the initial game state and units."""
        print("Initializing game...")
        # Player 1 setup
        self.unit_module.create_unit("P1_King", "player1", "King", (0, 0))
        self.unit_module.create_unit("P1_Pawn1", "player1", "Pawn", (0, 1))
        self.unit_module.create_unit("P1_Rook1", "player1", "Rook", (0, 7))
        self.fog_of_war_module.initialize_player_map("player1")

        # Player 2 setup
        self.unit_module.create_unit("P2_King", "player2", "King", (7, 7))
        self.unit_module.create_unit("P2_Pawn1", "player2", "Pawn", (7, 6))
        self.unit_module.create_unit("P2_Rook1", "player2", "Rook", (7, 0))
        self.fog_of_war_module.initialize_player_map("player2")

        # Initial card distribution (dummy data for now)
        self.card_system_module.initialize_player_hand("player1", ["morale_boost", "scouting_report"])
        self.card_system_module.initialize_player_hand("player2", ["morale_boost"]) # Less cards for simplicity

        # Perform initial fog of war revelation around Kings
        for player_id in self.players:
            king_unit = self.unit_module.get_king_unit(player_id)
            if king_unit:
                self.fog_of_war_module.reveal_area(player_id, king_unit.position, king_unit.hq_visual_range)
        print("Game initialization complete. Entering Opening (Planning) Phase.")
        self.current_phase = "Opening"

    def start_planning_phase(self):
        """Placeholder for planning phase logic."""
        print("Current Phase: Opening (Planning)")
        # In a real game, this would involve UI interaction for setting behaviors, formations, goals
        # For this skeletal code, we'll auto-set some basic behaviors
        for unit in self.unit_module.get_all_active_units():
            unit.behavior_patterns = {
                'movement': 'aggressive',
                'engagement': 'engage_all'
            }
            if unit.unit_type == "King":
                # King moves to random central spot as a placeholder order
                unit.current_orders.append({"type": "move_to", "target_pos": [random.randint(1,6), random.randint(1,6)]})

    def confirm_readiness(self):
        """Transition to Battle Phase upon player readiness."""
        print("Confirming readiness. Transitioning to Battle Phase...")
        self.current_phase = "Battle"
        self.game_running = True

    def game_loop_tick(self):
        """Executes one tick of the real-time game loop."""
        if not self.game_running:
            return

        self.tick_count += 1
        # print(f"Game Tick: {self.tick_count}") # Uncomment for verbose tick logging

        # 1. Update Units (movement, behavior execution)
        self.unit_module.update_units(self)

        # 2. Update Messengers (movement, delivery, risk)
        self.messenger_module.update_messengers(self)

        # 3. Update Combat (resolve ongoing engagements)
        self.combat_module.update_combat(self)

        # 4. Update Fog of War (unit vision, reports)
        for unit in self.unit_module.get_all_active_units():
            self.fog_of_war_module.update_player_map_from_unit_vision(unit.player_id, unit, self.battlefield_module)
            # Simulate units sending reports periodically
            # Every 5 seconds (GAME_TICK_RATE * 5 ticks) and not for Kings
            if self.tick_count % (GAME_TICK_RATE * 5) == 0 and not unit.is_king:
                report_content = {
                    "unit_id": unit.id,
                    "hp": unit.hp,
                    "morale": unit.morale,
                    "position": unit.position,
                    "visibility_update": [[x,y,True] for y in range(unit.position[1]-unit.sight_range, unit.position[1]+unit.sight_range+1)
                                          for x in range(unit.position[0]-unit.sight_range, unit.position[0]+unit.sight_range+1)
                                          if self.battlefield_module.is_within_bounds((x,y))]
                }
                self.messenger_module.dispatch_messenger(
                    f"report_from_{unit.id}",
                    unit.player_id,
                    unit.position,
                    self.unit_module.get_king_unit(unit.player_id).id,
                    report_content,
                    is_report=True
                )

        # 5. Update Card Effects (durations, removal)
        self.card_system_module.update_card_effects(self)

        # 6. Check Game End Conditions
        self.check_game_end()

    def check_game_end(self):
        """Checks if any player's King has been defeated."""
        king1_alive = self.unit_module.get_king_unit("player1").is_alive
        king2_alive = self.unit_module.get_king_unit("player2").is_alive

        if not king1_alive:
            print("Player 1's King has fallen! Player 2 wins!")
            self.game_running = False
            self.current_phase = "Game_Over"
        elif not king2_alive:
            print("Player 2's King has fallen! Player 1 wins!")
            self.game_running = False
            self.current_phase = "Game_Over"

    def run(self):
        """Main entry point to start the game loop."""
        self.initialize_game()
        self.start_planning_phase()

        # Simulate user confirmation to transition to battle phase
        print("\n--- Simulating Player Readiness Confirmation ---\n")
        time.sleep(2) # Give a moment to read the messages
        self.confirm_readiness()

        # Main game loop for the Battle Phase
        tick_interval = 1.0 / GAME_TICK_RATE
        while self.game_running:
            self.game_loop_tick()
            time.sleep(tick_interval)

            # Example: Simulate a player dispatching an order after some ticks
            if self.tick_count == GAME_TICK_RATE * 3: # After 3 seconds
                print("\n--- Simulating Player 1 dispatching an order ---\n")
                king1 = self.unit_module.get_king_unit("player1")
                # Target an enemy unit (P2_Pawn1) as an example target for the order
                target_enemy_unit = self.unit_module.get_unit_by_id("P2_Pawn1")
                if king1 and target_enemy_unit and target_enemy_unit.is_alive:
                    # Order P1's Pawn1 to attack P2's Pawn1
                    self.messenger_module.dispatch_messenger(
                        "order_p1",
                        "player1",
                        king1.position,
                        "P1_Pawn1", # The unit receiving the order
                        {"type": "attack_unit", "target_unit_id": target_enemy_unit.id}
                    )
            # Example: Simulate a card usage
            if self.tick_count == GAME_TICK_RATE * 5: # After 5 seconds
                print("\n--- Simulating Player 1 using a card ---\n")
                if "morale_boost" in self.card_system_module.player_hands.get("player1", []):
                    self.card_system_module.play_card("player1", "morale_boost", "P1_Pawn1")

            # Break loop early for demonstration if game isn't dynamic enough
            if self.tick_count > GAME_TICK_RATE * 10 and self.game_running: # Stop after 10 seconds if still running
                 print("\n--- Simulation end (for demonstration purposes). ---\n")
                 self.game_running = False

