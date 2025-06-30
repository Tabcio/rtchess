# real_time_chess/src/modules/card_system_module.py

# You would ideally load CARD_DEFINITIONS from data/card_definitions.json
# For now, it's defined here as a placeholder for self-containment.
CARD_DEFINITIONS = {
    "morale_boost": {
        "name": "Morale Boost",
        "description": "Temporarily increases a unit's morale, improving combat effectiveness.",
        "phase": "active_phase",
        "cost": 50, # Example resource cost
        "effect_type": "unit_buff",
        "effect_params": {"attribute": "morale", "value": 20, "duration": 30}, # duration in seconds
        "target_type": "single_unit"
    },
    "scouting_report": {
        "name": "Scouting Report",
        "description": "Reveals a larger area of the map initially.",
        "phase": "planning_phase",
        "cost": 0,
        "effect_type": "map_reveal",
        "effect_params": {"radius": 5},
        "target_type": "area"
    },
    "rapid_dispatch": {
        "name": "Rapid Dispatch",
        "description": "Messengers travel faster for a short period.",
        "phase": "active_phase",
        "cost": 25,
        "effect_type": "messenger_buff",
        "effect_params": {"attribute": "speed_modifier", "value": 2.0, "duration": 15}, # 2x speed for 15s
        "target_type": "player"
    }
}

# Assuming GAME_TICK_RATE might be needed for duration conversions
# from ..utils.constants import GAME_TICK_RATE # Uncomment when constants.py is ready
GAME_TICK_RATE = 20 # Placeholder

class CardSystemModule:
    """
    Manages playing cards, including player hands, card usage, and the application
    and management of active card effects.
    """
    def __init__(self):
        """
        Initializes the CardSystemModule.
        Stores player hands and a list of currently active card effects.
        """
        self.player_hands = {} # {player_id: [card_id1, card_id2, ...]}
        # Stores active effects: [{card_id, target_id, duration_left_ticks, effect_params, player_id}]
        self.active_card_effects = []
        print("CardSystemModule initialized.")

    def initialize_player_hand(self, player_id: str, initial_cards: list):
        """
        Gives a player their starting set of cards.

        Args:
            player_id (str): The ID of the player.
            initial_cards (list): A list of card IDs to add to the player's hand.
        """
        self.player_hands[player_id] = list(initial_cards)
        print(f"Player '{player_id}' received initial cards: {self.player_hands[player_id]}.")

    def play_card(self, game_state, player_id: str, card_id: str, target_id: str = None) -> bool:
        """
        Allows a player to use a card from their hand.

        Args:
            game_state: A reference to the main Game object to access other modules.
            player_id (str): The ID of the player attempting to play the card.
            card_id (str): The ID of the card to play.
            target_id (str, optional): The ID of the unit or entity the card targets, if any.

        Returns:
            bool: True if the card was successfully played, False otherwise.
        """
        if card_id not in self.player_hands.get(player_id, []):
            print(f"Player '{player_id}' does not have card '{card_id}'.")
            return False

        card_info = CARD_DEFINITIONS.get(card_id)
        if not card_info:
            print(f"Error: Card '{card_id}' is not defined in CARD_DEFINITIONS.")
            return False

        # TODO: Implement resource cost check (e.g., if players have "Command Points")
        # if game_state.player_resources[player_id] < card_info['cost']:
        #     print(f"Player '{player_id}' does not have enough resources to play '{card_id}'.")
        #     return False

        # Check phase validity (e.g., can't play 'active_phase' card in 'planning_phase')
        if card_info['phase'] != game_state.current_phase.lower().replace(" ", "_"):
             print(f"Cannot play '{card_id}' in current phase ({game_state.current_phase}). Card phase: {card_info['phase']}.")
             return False

        # Remove card from player's hand
        self.player_hands[player_id].remove(card_id)
        print(f"Player '{player_id}' played card: '{card_info['name']}'.")

        # Apply the card's effect
        self.apply_card_effect(game_state, card_info, player_id, target_id)
        return True

    def apply_card_effect(self, game_state, card_info: dict, player_id: str, target_id: str = None):
        """
        Applies the specific effect of a card to the game state or target entities.

        Args:
            game_state: A reference to the main Game object.
            card_info (dict): The dictionary containing the card's definition.
            player_id (str): The ID of the player who played the card.
            target_id (str, optional): The ID of the unit or entity the card targets.
        """
        effect_type = card_info["effect_type"]
        effect_params = card_info["effect_params"]

        if effect_type == "unit_buff":
            target_unit = game_state.unit_module.get_unit_by_id(target_id)
            if target_unit and target_unit.is_alive and target_unit.player_id == player_id:
                # Store the effect to be applied over time or immediately modify unit stats
                self.active_card_effects.append({
                    "card_id": card_info["card_id"],
                    "target_id": target_id,
                    "duration_left_ticks": effect_params["duration"] * GAME_TICK_RATE, # Convert seconds to ticks
                    "effect_params": effect_params,
                    "player_id": player_id # Store player ID for context
                })
                print(f"  Applying '{card_info['name']}' effect to unit '{target_id}'.")
                # Immediate effect application example: Morale Boost
                if effect_params["attribute"] == "morale":
                    target_unit.morale = min(100, target_unit.morale + effect_params["value"])
                    print(f"  Unit '{target_id}' morale increased to {target_unit.morale}.")
            else:
                print(f"  Card effect failed: Target unit '{target_id}' invalid or not owned by player.")

        elif effect_type == "map_reveal":
            king_unit = game_state.unit_module.get_king_unit(player_id)
            if king_unit:
                game_state.fog_of_war_module.reveal_area(player_id, king_unit.position, effect_params["radius"])
                print(f"  Map revealed for player '{player_id}' via '{card_info['name']}'.")
            else:
                print(f"  Card effect failed: Player '{player_id}' King not found for map reveal.")

        elif effect_type == "messenger_buff":
            # This effect is applied to the player's messengers
            # We'll activate it in update_card_effects, but mark it here.
            self.active_card_effects.append({
                "card_id": card_info["card_id"],
                "target_id": player_id, # Target is the player
                "duration_left_ticks": effect_params["duration"] * GAME_TICK_RATE,
                "effect_params": effect_params,
                "player_id": player_id
            })
            print(f"  '{card_info['name']}' activated for player '{player_id}'s messengers.")

        # TODO: Add more effect types (e.g., unit_spawn, terrain_change, combat_modifier)

    def update_card_effects(self, game_state):
        """
        Updates the duration of active card effects and removes expired ones.
        Also applies ongoing effects (like messenger speed buffs).

        Args:
            game_state: A reference to the main Game object.
        """
        effects_to_remove = []
        for effect in list(self.active_card_effects): # Iterate over a copy
            effect["duration_left_ticks"] -= 1

            # Apply ongoing effects
            if effect["effect_params"]["attribute"] == "speed_modifier" and effect["target_id"] == effect["player_id"]:
                # This would typically modify a global messenger speed for the player in MessengerModule
                # For now, it's just a log. You'd pass this modifier to MessengerModule for calculations.
                # print(f"  Player '{effect['player_id']}' messenger speed modified by x{effect['effect_params']['value']}.")
                pass # The actual speed modification would be handled in MessengerModule

            if effect["duration_left_ticks"] <= 0:
                effects_to_remove.append(effect)
                print(f"  Card effect '{effect['card_id']}' on target '{effect['target_id']}' expired.")
                # TODO: Revert the effect (e.g., revert morale change, remove speed buff)
                if effect["effect_params"]["attribute"] == "morale":
                    target_unit = game_state.unit_module.get_unit_by_id(effect["target_id"])
                    if target_unit and target_unit.is_alive:
                        # Simple reversion: subtract value. In reality, track base morale.
                        target_unit.morale = max(0, target_unit.morale - effect["effect_params"]["value"])
                        print(f"  Unit '{target_unit.id}' morale reverted to {target_unit.morale}.")


        for effect in effects_to_remove:
            self.active_card_effects.remove(effect)


# Example usage for testing this file directly
if __name__ == "__main__":
    print("--- Testing CardSystemModule ---")

    # Mock dependent classes for standalone testing
    class MockUnit:
        def __init__(self, unit_id, player_id, pos, is_king=False, morale=100, is_alive=True):
            self.id = unit_id
            self.player_id = player_id
            self.position = list(pos)
            self.is_king = is_king
            self.is_alive = is_alive
            self.morale = morale
            self.hq_visual_range = 5 # For kings

    class MockUnitModule:
        def __init__(self):
            self.units = {
                "P1_King": MockUnit("P1_King", "player1", [0, 0], True),
                "P1_Pawn1": MockUnit("P1_Pawn1", "player1", [1, 1], morale=80),
            }
        def get_unit_by_id(self, unit_id):
            return self.units.get(unit_id)
        def get_king_unit(self, player_id):
            for unit in self.units.values():
                if unit.player_id == player_id and unit.is_king:
                    return unit
            return None

    class MockFogOfWarModule:
        def reveal_area(self, player_id, center_pos, radius):
            print(f"  FOW: Player '{player_id}' map revealed around {center_pos} with radius {radius}.")

    class MockGame:
        def __init__(self):
            self.unit_module = MockUnitModule()
            self.fog_of_war_module = MockFogOfWarModule()
            self.current_phase = "battle" # For testing active phase cards
            print("MockGame initialized for CardSystemModule testing.")

    mock_game = MockGame()
    card_manager = CardSystemModule()

    player1_id = "player1"
    player2_id = "player2"

    card_manager.initialize_player_hand(player1_id, ["morale_boost", "scouting_report", "rapid_dispatch"])
    card_manager.initialize_player_hand(player2_id, ["morale_boost"])

    print(f"\nPlayer 1's hand: {card_manager.player_hands.get(player1_id)}")

    # Test playing a card (Morale Boost)
    print("\nPlayer 1 playing 'morale_boost' on P1_Pawn1:")
    p1_pawn1 = mock_game.unit_module.get_unit_by_id("P1_Pawn1")
    print(f"  P1_Pawn1 initial morale: {p1_pawn1.morale}")
    card_manager.play_card(mock_game, player1_id, "morale_boost", "P1_Pawn1")
    print(f"  P1_Pawn1 morale after card: {p1_pawn1.morale}")
    print(f"  Player 1's hand after playing: {card_manager.player_hands.get(player1_id)}")
    print(f"  Active card effects: {card_manager.active_card_effects}")


    # Test playing a card (Scouting Report - Planning Phase card, won't work in battle phase)
    print("\nPlayer 1 attempting to play 'scouting_report' (Planning Phase card):")
    card_manager.play_card(mock_game, player1_id, "scouting_report", "P1_King")


    # Change mock game phase to 'planning' for scouting report test
    mock_game.current_phase = "planning_phase"
    print("\nChanging game phase to 'planning_phase'. Player 1 playing 'scouting_report':")
    card_manager.play_card(mock_game, player1_id, "scouting_report", "P1_King")
    print(f"  Player 1's hand after playing: {card_manager.player_hands.get(player1_id)}")


    # Test playing a Messenger Buff card
    mock_game.current_phase = "battle" # Back to battle for this card
    print("\nPlayer 1 playing 'rapid_dispatch':")
    card_manager.play_card(mock_game, player1_id, "rapid_dispatch", player1_id)
    print(f"  Active card effects: {card_manager.active_card_effects}")

    # Simulate ticks to see effects update and expire
    print("\nSimulating game ticks to expire card effects:")
    for i in range(1, 35): # Enough ticks for Morale Boost (30s * 20ticks/s = 600 ticks) and Rapid Dispatch (15s * 20 = 300 ticks)
        if i % 100 == 0:
            print(f"--- Tick {i} ---")
        card_manager.update_card_effects(mock_game)
        if not card_manager.active_card_effects:
            print(f"All card effects expired after {i} ticks.")
            break

    print(f"\nP1_Pawn1 morale after effect expiration: {p1_pawn1.morale}")
    print(f"Final active card effects: {card_manager.active_card_effects}")

    print("\n--- End of CardSystemModule Test ---")
