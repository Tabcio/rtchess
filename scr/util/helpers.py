# real_time_chess/src/utils/helpers.py

import math
import random

def calculate_distance(pos1: list, pos2: list) -> float:
    """
    Calculates the Euclidean distance between two [x, y] coordinates.

    Args:
        pos1 (list): The first position [x, y].
        pos2 (list): The second position [x, y].

    Returns:
        float: The Euclidean distance.
    """
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamps a value between a minimum and maximum limit.

    Args:
        value (float): The value to clamp.
        min_val (float): The minimum allowed value.
        max_val (float): The maximum allowed value.

    Returns:
        float: The clamped value.
    """
    return max(min_val, min(value, max_val))

def roll_dice(num_dice: int, sides: int) -> int:
    """
    Simulates rolling multiple dice.

    Args:
        num_dice (int): The number of dice to roll.
        sides (int): The number of sides on each die.

    Returns:
        int: The sum of the dice rolls.
    """
    total = 0
    for _ in range(num_dice):
        total += random.randint(1, sides)
    return total

def get_neighbors_4_directions(position: list) -> list[list]:
    """
    Returns the 4 direct (non-diagonal) neighbors of a given grid position.

    Args:
        position (list): The [x, y] coordinates.

    Returns:
        list[list]: A list of neighbor [x, y] coordinates.
    """
    x, y = position
    return [
        [x, y + 1],  # Down
        [x, y - 1],  # Up
        [x + 1, y],  # Right
        [x - 1, y]   # Left
    ]

def get_neighbors_8_directions(position: list) -> list[list]:
    """
    Returns the 8 (including diagonal) neighbors of a given grid position.

    Args:
        position (list): The [x, y] coordinates.

    Returns:
        list[list]: A list of neighbor [x, y] coordinates.
    """
    x, y = position
    return [
        [x, y + 1], [x, y - 1], [x + 1, y], [x - 1, y],  # 4-directions
        [x + 1, y + 1], [x - 1, y - 1], [x + 1, y - 1], [x - 1, y + 1] # Diagonals
    ]

# Example usage for testing this file directly
if __name__ == "__main__":
    print("--- Testing Helpers Module ---")

    # Test calculate_distance
    pos_a = [0, 0]
    pos_b = [3, 4]
    distance = calculate_distance(pos_a, pos_b)
    print(f"Distance between {pos_a} and {pos_b}: {distance} (Expected: 5.0)")
    assert distance == 5.0, "calculate_distance failed"

    # Test clamp
    clamped_val_1 = clamp(10, 0, 5)
    clamped_val_2 = clamp(-2, 0, 5)
    clamped_val_3 = clamp(3, 0, 5)
    print(f"Clamping 10 between 0 and 5: {clamped_val_1} (Expected: 5)")
    print(f"Clamping -2 between 0 and 5: {clamped_val_2} (Expected: 0)")
    print(f"Clamping 3 between 0 and 5: {clamped_val_3} (Expected: 3)")
    assert clamped_val_1 == 5 and clamped_val_2 == 0 and clamped_val_3 == 3, "clamp failed"

    # Test roll_dice
    roll_result = roll_dice(2, 6)
    print(f"Rolling 2d6: {roll_result} (Expected: between 2 and 12)")
    assert 2 <= roll_result <= 12, "roll_dice failed"

    # Test get_neighbors_4_directions
    neighbors_4 = get_neighbors_4_directions([2, 2])
    print(f"Neighbors (4-directions) of [2,2]: {neighbors_4}")
    assert len(neighbors_4) == 4, "get_neighbors_4_directions failed"
    assert [2,3] in neighbors_4 and [2,1] in neighbors_4 and [3,2] in neighbors_4 and [1,2] in neighbors_4, "get_neighbors_4_directions failed"

    # Test get_neighbors_8_directions
    neighbors_8 = get_neighbors_8_directions([2, 2])
    print(f"Neighbors (8-directions) of [2,2]: {neighbors_8}")
    assert len(neighbors_8) == 8, "get_neighbors_8_directions failed"
    assert [3,3] in neighbors_8 and [1,1] in neighbors_8, "get_neighbors_8_directions failed for diagonals"

    print("\n--- End of Helpers Module Test ---")
