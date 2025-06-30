# real_time_chess/src/modules/messenger_module.py

import random

# Import Messenger entity from the entities sub-package
from ..core.entities.messenger import Messenger

class MessengerModule:
    """
    Manages all messenger entities in the game.
    Responsibilities include dispatching new messengers, updating their movement,
    calculating their risk of interception, and handling their delivery.
    """
    def __init__(self):
        """
        Initializes the MessengerModule.
        Stores all active messenger objects.
        """
        self.active_messengers = {} # Dictionary to store active Messenger objects: {messenger_id: Messenger_object}
        self.next_messenger_id = 0 # Counter for generating unique messenger IDs
        print("MessengerModule initialized.")

    def dispatch_messenger(self, msg_id_prefix: str, player_id: str, origin_pos: list, target_entity_id: str, payload_data: dict, is_report: bool = False):
        """
        Creates and dispatches a new messenger.

        Args:
            msg_id_prefix (str): A prefix for the messenger ID (e.g., "order_m", "report_m").
            player_id (str): The ID of the player who owns this messenger.
            origin_pos (list): The [x, y] coordinates where the messenger starts its journey.
            target_entity_id (str): The ID of the unit (or King) this messenger is traveling to.
            payload_data (dict): The data being carried (either an order or a report).
            is_report (bool): True if this messenger is carrying a report back to HQ, False for an order.

        Returns:
            Messenger: The newly created Messenger object.
        """
        msg_id = f"{msg_id_prefix}_{self.next_messenger_id}"
        self.next_messenger_id += 1

        messenger = Messenger(msg_id, player_id, origin_pos, target_entity_id, payload_data, is_report)
        self.active_messengers[messenger.id] = messenger

        # Immediately calculate the path for the messenger
        # This requires access to the target unit's position via the game state
        # In the main game loop, `messenger.update` will handle its movement
        # For dispatch, we need the target's current position to set the path
        # This assumes the game_state is available or passed during dispatch
        # For initial setup, the messenger itself needs to resolve its target position.
        # This is a bit of a circular dependency if not careful, so will modify Messenger to take target_pos too.
        # For now, Messenger will fetch target position through mock_game.unit_module in its test.
        print(f"Messenger '{messenger.id}' dispatched from {origin_pos} towards '{target_entity_id}'.")
        return messenger

    def update_messengers(self, game_state):
        """
        Updates all active messengers for the current game tick.
        This involves their movement, risk checks, and delivery attempts.

        Args:
            game_state: A reference to the main Game object to access other modules.
        """
        messengers_to_remove = []
        for messenger_id, messenger in list(self.active_messengers.items()): # Iterate over a copy
            if messenger.is_active:
                # Ensure the messenger has its path calculated
                if not messenger.path:
                    # Try to get target position from game_state.unit_module
                    target_unit = game_state.unit_module.get_unit_by_id(messenger.target_entity_id)
                    if target_unit and target_unit.is_alive:
                        messenger.calculate_path(game_state.battlefield_module, target_unit.position)
                    else:
                        print(f"Messenger {messenger.id}: Target unit {messenger.target_entity_id} not found or dead. Deactivating.")
                        messenger.is_active = False # Deactivate if target is gone

                if messenger.is_active: # Check again after path calculation
                    messenger.update(game_state)
                    if not messenger.is_active: # If messenger became inactive during update (e.g., delivered or died)
                        messengers_to_remove.append(messenger_id)
            else: # Messenger already inactive
                messengers_to_remove.append(messenger_id)

        for msg_id in messengers_to_remove:
            if msg_id in self.active_messengers:
                del self.active_messengers[msg_id]
                # print(f"Removed inactive messenger: {msg_id}.")

    def get_messenger_risk(self, origin_pos: list, current_pos: list, battlefield_module) -> float:
        """
        Calculates the probability of a messenger being intercepted or killed
        based on its journey. This is a placeholder for a more complex calculation.

        Args:
            origin_pos (list): The starting position of the messenger.
            current_pos (list): The messenger's current position.
            battlefield_module: Reference to the BattlefieldModule for terrain/enemy info.

        Returns:
            float: A float between 0.0 and 1.0 representing the risk.
        """
        # TODO: Implement more sophisticated risk calculation
        # Factors to consider:
        # - Distance traveled (longer distance = higher risk)
        # - Terrain traversed (e.g., forest might offer cover, open plains higher risk)
        # - Proximity to enemy units (higher risk if near enemies)
        # - Presence of enemy units specifically designed to intercept messengers

        distance_traveled = ((origin_pos[0] - current_pos[0])**2 + (origin_pos[1] - current_pos[1])**2)**0.5
        base_risk_per_tile = 0.005 # Example: 0.5% risk per tile

        # Simple linear risk for now
        risk = distance_traveled * base_risk_per_tile
        return min(risk, 0.95) # Cap risk at 95%


# Example usage for testing this file directly
if __name__ == "__main__":
    print("--- Testing MessengerModule ---")

    # Mock dependent classes for standalone testing
    class MockUnit:
        def __init__(self, unit_id, player_id, pos, is_king=False, is_alive=True):
            self.id = unit_id
            self.player_id = player_id
            self.position = list(pos)
            self.is_king = is_king
            self.is_alive = is_alive
            self.current_orders = [] # To receive orders
            self.sight_range = 5 if is_king else 2 # A basic sight range

    class MockUnitModule:
        def __init__(self):
            self.units = {
                "P1_King": MockUnit("P1_King", "player1", [0, 0], True),
                "P1_Pawn1": MockUnit("P1_Pawn1", "player1", [1, 1]),
                "P2_King": MockUnit("P2_King", "player2", [7, 7], True),
                "P2_Pawn1": MockUnit("P2_Pawn1", "player2", [6, 6]),
            }
        def get_unit_by_id(self, unit_id):
            return self.units.get(unit_id)
        def get_king_unit(self, player_id):
            for unit in self.units.values():
                if unit.player_id == player_id and unit.is_king:
                    return unit
            return None

    class MockBattlefieldModule:
        def __init__(self):
            self.size = (8, 8)
        def is_within_bounds(self, pos):
            x, y = pos
            return 0 <= x < self.size[0] and 0 <= y < self.size[1]
        def get_terrain_at(self, pos):
            return {"movement_modifier": 1.0, "visibility_modifier": 1.0, "combat_modifier": 1.0} # Simplified mock

    class MockFogOfWarModule:
        def update_player_map_from_report(self, player_id, report_data):
            # print(f"Fog of War updated for {player_id} with report from {report_data.get('unit_id', 'Unknown')}.")
            pass # Suppress print for cleaner output

    # Full MockGame class to pass to messenger.update
    class MockGame:
        def __init__(self):
            self.unit_module = MockUnitModule()
            self.battlefield_module = MockBattlefieldModule()
            self.fog_of_war_module = MockFogOfWarModule()
            self.messenger_module = None # This will be set by the test itself
            print("MockGame initialized for MessengerModule testing.")

    mock_game_instance = MockGame()
    messenger_manager = MessengerModule()
    mock_game_instance.messenger_module = messenger_manager # Set the reference

    print("\nDispatching an order messenger from P1_King to P1_Pawn1 (move order):")
    king1 = mock_game_instance.unit_module.get_king_unit("player1")
    pawn1 = mock_game_instance.unit_module.get_unit_by_id("P1_Pawn1")

    order_payload = {"type": "move_to", "target_pos": [5, 5]}
    order_messenger_obj = messenger_manager.dispatch_messenger(
        "order_m", "player1", king1.position, pawn1.id, order_payload, is_report=False
    )
    # The messenger itself needs its path calculated BEFORE its update loop.
    # In the real game, this might be handled within dispatch_messenger if it had access to unit_module
    # For now, simulate calculation here
    order_messenger_obj.calculate_path(mock_game_instance.battlefield_module, pawn1.position)


    print("\nSimulating messenger updates (order delivery):")
    for i in range(1, 10): # Simulate a few ticks
        print(f"--- Tick {i} ---")
        messenger_manager.update_messengers(mock_game_instance)
        if not order_messenger_obj.is_active:
            print(f"Order messenger inactive after {i} ticks.")
            break

    print(f"\nP1_Pawn1's orders after messenger activity: {pawn1.current_orders}")

    # Test report messenger
    print("\nDispatching a report messenger from P2_Pawn1 to P2_King:")
    pawn2 = mock_game_instance.unit_module.get_unit_by_id("P2_Pawn1")
    king2 = mock_game_instance.unit_module.get_king_unit("player2")
    report_payload = {
        "unit_id": pawn2.id,
        "hp": pawn2.hp,
        "position": pawn2.position,
        "visibility_update": [[pawn2.position[0], pawn2.position[1], True]]
    }
    report_messenger_obj = messenger_manager.dispatch_messenger(
        "report_m", "player2", pawn2.position, king2.id, report_payload, is_report=True
    )
    report_messenger_obj.calculate_path(mock_game_instance.battlefield_module, king2.position)


    print("\nSimulating messenger updates (report delivery):")
    for i in range(1, 10): # Simulate a few ticks
        print(f"--- Tick {i} ---")
        messenger_manager.update_messengers(mock_game_instance)
        if not report_messenger_obj.is_active:
            print(f"Report messenger inactive after {i} ticks.")
            break

    print("\n--- End of MessengerModule Test ---")
