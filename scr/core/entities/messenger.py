# real_time_chess/src/core/entities/messenger.py

import random

class Messenger:
    """
    Represents a messenger entity traveling between a King's Headquarters and units.
    Messengers are used to dispatch orders and deliver unit reports.
    They can be intercepted or killed during transit.
    """
    def __init__(self, msg_id: str, player_id: str, origin_pos: list, target_entity_id: str, payload_data: dict, is_report: bool = False):
        """
        Initializes a new messenger.

        Args:
            msg_id (str): A unique identifier for this messenger instance.
            player_id (str): The ID of the player who owns this messenger.
            origin_pos (list): The [x, y] coordinates where the messenger starts its journey.
            target_entity_id (str): The ID of the unit (or King) this messenger is traveling to.
            payload_data (dict): The data being carried (either an order or a report).
            is_report (bool): True if this messenger is carrying a report back to HQ, False for an order.
        """
        self.id = msg_id
        self.player_id = player_id
        self.origin_pos = list(origin_pos)
        self.target_entity_id = target_entity_id # Can be a unit ID or King's ID
        self.payload_data = payload_data
        self.is_report = is_report

        self.current_pos = list(origin_pos) # Messenger's current position
        self.path = [] # List of [x, y] coordinates the messenger will traverse
        self.health = 10 # Messengers can be targeted and destroyed
        self.speed = 2 # Tiles per game tick (placeholder)
        self.is_active = True # False if messenger has delivered, died, or target is invalid

    def calculate_path(self, battlefield_module, target_pos: list):
        """
        Calculates the path the messenger will take from its origin to the target.
        This will eventually use a proper pathfinding algorithm.

        Args:
            battlefield_module: Reference to the BattlefieldModule to get board info.
            target_pos (list): The [x, y] coordinates of the messenger's destination.
        """
        if not battlefield_module.is_within_bounds(target_pos):
            print(f"Messenger {self.id}: Target position {target_pos} out of bounds. Deactivating.")
            self.is_active = False
            return

        # TODO: Implement a real pathfinding algorithm (e.g., A* from utils/pathfinding.py)
        # For now, a very simplistic direct line path (only start and end points)
        self.path = [list(self.origin_pos), list(target_pos)]
        if self.origin_pos != target_pos:
            print(f"Messenger {self.id}: Path calculated from {self.origin_pos} to {target_pos}.")
        else:
            print(f"Messenger {self.id}: Already at target position {target_pos}.")
            self.is_active = False # Already there, no movement needed

    def update(self, game_state):
        """
        Updates the messenger's state each game tick, including movement and risk checks.

        Args:
            game_state: A reference to the main Game object to access other modules.
        """
        if not self.is_active or self.health <= 0:
            if not self.is_active:
                # print(f"Messenger {self.id} is inactive.")
                pass
            if self.health <= 0:
                print(f"Messenger {self.id} was destroyed while en route!")
                self.is_active = False # Ensure it's marked inactive
            return

        # Simple movement simulation: move towards the next point in the path
        if len(self.path) > 1:
            # Assuming path contains [current_pos, next_step, ..., final_target]
            # For this simple model, we just jump to the 'final target' to simulate instant travel for now
            # In a real game, you would increment current_pos step by step based on speed
            target_node = self.path[-1] # The actual destination
            current_x, current_y = self.current_pos
            target_x, target_y = target_node

            # Move one step towards the target (simplistic for skeletal)
            moved = False
            if current_x < target_x:
                self.current_pos[0] += 1
                moved = True
            elif current_x > target_x:
                self.current_pos[0] -= 1
                moved = True

            if current_y < target_y:
                self.current_pos[1] += 1
                moved = True
            elif current_y > target_y:
                self.current_pos[1] -= 1
                moved = True

            # If arrived at the target node (or if it was a direct jump in a simpler path)
            if self.current_pos == target_node:
                self.deliver(game_state)
                self.is_active = False
            elif moved:
                # print(f"Messenger {self.id} moving. Current Pos: {self.current_pos}")
                # TODO: Implement risk calculation here (e.g., check for enemies along the path)
                # Messenger risk calculation example (very basic):
                risk = game_state.messenger_module.get_messenger_risk(self.origin_pos, self.current_pos, game_state.battlefield_module)
                if random.random() < risk: # Small chance to die based on risk
                    self.health = 0
                    print(f"Messenger {self.id} intercepted! Health depleted.")
                    self.is_active = False # Messenger killed
        elif self.current_pos == self.path[0] and len(self.path) == 1:
            # Already at the single-point target or just created at target, deliver immediately
            self.deliver(game_state)
            self.is_active = False
        else:
            # No path or invalid state, deactivate
            self.is_active = False
            print(f"Messenger {self.id} inactive due to pathing issue or completion.")


    def deliver(self, game_state):
        """
        Delivers the messenger's payload (order or report) to the target entity.
        """
        if not self.is_active or self.health <= 0:
            return

        target_entity = game_state.unit_module.get_unit_by_id(self.target_entity_id)

        if not target_entity or not target_entity.is_alive:
            print(f"Messenger {self.id}: Target unit {self.target_entity_id} not found or dead. Delivery failed.")
            return

        if self.is_report:
            # Report delivered to King
            print(f"Messenger {self.id} delivered report to King ({target_entity.id}). Content: {self.payload_data.get('unit_id', 'Unknown Unit')}'s report.")
            game_state.fog_of_war_module.update_player_map_from_report(self.player_id, self.payload_data)
        else:
            # Order delivered to Unit
            target_entity.current_orders.append(self.payload_data)
            print(f"Messenger {self.id} delivered order to unit {target_entity.id}. Order: {self.payload_data.get('type', 'Unknown Order Type')}.")
            # Dispatch a return messenger to confirm order receipt
            game_state.messenger_module.dispatch_messenger(
                f"return_msg_{target_entity.id}",
                self.player_id,
                target_entity.position,
                game_state.unit_module.get_king_unit(self.player_id).id,
                {"status": "Order Received", "unit_id": target_entity.id, "order_hash": hash(str(self.payload_data))}, # Simple confirmation payload
                is_report=True
            )


# Example usage for testing this file directly
if __name__ == "__main__":
    print("--- Testing Messenger Class ---")

    # Mock dependent modules for standalone testing
    class MockUnit:
        def __init__(self, unit_id, player_id, pos, is_king=False):
            self.id = unit_id
            self.player_id = player_id
            self.position = list(pos)
            self.is_king = is_king
            self.is_alive = True
            self.current_orders = []
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

    class MockFogOfWarModule:
        def update_player_map_from_report(self, player_id, report_data):
            print(f"Fog of War updated for {player_id} with report from {report_data.get('unit_id', 'Unknown')}.")

    class MockMessengerModule:
        def __init__(self):
            self.messengers = {}
            self.next_id = 0
        def dispatch_messenger(self, msg_id_prefix, player_id, origin_pos, target_unit_id, order_data, is_report):
            msg_id = f"{msg_id_prefix}_{self.next_id}"
            self.next_id += 1
            messenger = Messenger(msg_id, player_id, origin_pos, target_unit_id, order_data, is_report)
            self.messengers[messenger.id] = messenger
            messenger.calculate_path(mock_game.battlefield_module, mock_game.unit_module.get_unit_by_id(target_unit_id).position)
            return messenger
        def get_messenger_risk(self, origin, current, battlefield_module):
            # Very simple mock risk
            dist = ((origin[0]-current[0])**2 + (origin[1]-current[1])**2)**0.5
            return dist * 0.01 # 1% risk per tile

    class MockGame:
        def __init__(self):
            self.unit_module = MockUnitModule()
            self.battlefield_module = MockBattlefieldModule()
            self.fog_of_war_module = MockFogOfWarModule()
            self.messenger_module = MockMessengerModule()
            # Link messenger_module's internal messengers to this mock game for update calls
            self.messenger_module.mock_game_ref = self # Needed for messenger to call dispatch_messenger

    mock_game = MockGame()
    mock_game.messenger_module.mock_game_ref = mock_game # Set the circular reference for dispatch_messenger

    print("\nDispatching an order messenger from P1_King to P1_Pawn1:")
    king1_pos = mock_game.unit_module.get_king_unit("player1").position
    pawn1_pos = mock_game.unit_module.get_unit_by_id("P1_Pawn1").position

    # Create an order messenger
    order_messenger = Messenger(
        "order_m_001", "player1", king1_pos, "P1_Pawn1",
        {"type": "move_to", "target_pos": [3, 3]}, is_report=False
    )
    order_messenger.calculate_path(mock_game.battlefield_module, pawn1_pos)
    mock_game.messenger_module.messengers[order_messenger.id] = order_messenger


    print("\nSimulating messenger movement and delivery:")
    for i in range(5):
        print(f"\n--- Tick {i+1} ---")
        # In a real game loop, messenger_module.update_messengers would be called
        # Here, we're calling update on the specific messenger for demonstration
        if order_messenger.is_active:
            order_messenger.update(mock_game)
        else:
            print("Messenger has become inactive.")
            break

    p1_pawn1 = mock_game.unit_module.get_unit_by_id("P1_Pawn1")
    print(f"\nP1_Pawn1 current orders after messenger activity: {p1_pawn1.current_orders}")

    print("\n--- End of Messenger Class Test ---")
