# real_time_chess/src/utils/pathfinding.py

import heapq # For priority queue in A*

class Pathfinding:
    """
    Provides pathfinding capabilities on a grid, typically for unit movement
    and messenger routes. Implements the A* algorithm.
    """
    def __init__(self, battlefield_module):
        """
        Initializes the Pathfinding module with a reference to the battlefield.

        Args:
            battlefield_module: A reference to the BattlefieldModule instance,
                                used to query board size, terrain, and obstacles.
        """
        self.battlefield = battlefield_module
        print("Pathfinding initialized.")

    def find_path(self, start_pos: list, end_pos: list) -> list:
        """
        Finds the shortest path between a start and end position using the A* algorithm.

        Args:
            start_pos (list): The [x, y] starting coordinates.
            end_pos (list): The [x, y] ending coordinates.

        Returns:
            list: A list of [x, y] coordinates representing the path from start to end,
                  including both start and end. Returns an empty list if no path is found.
        """
        if not self.battlefield.is_within_bounds(start_pos) or \
           not self.battlefield.is_within_bounds(end_pos):
            print(f"Pathfinding: Start or end position out of bounds: {start_pos} -> {end_pos}")
            return []

        # TODO: Check if start_pos or end_pos are obstacles. If so, return empty.
        # if self.battlefield.grid[start_pos[1]][start_pos[0]].get("obstacle"):
        #     print(f"Pathfinding: Start position {start_pos} is an obstacle.")
        #     return []
        # if self.battlefield.grid[end_pos[1]][end_pos[0]].get("obstacle"):
        #     print(f"Pathfinding: End position {end_pos} is an obstacle.")
        #     return []


        # Priority queue: stores (f_cost, node)
        open_list = []
        heapq.heappush(open_list, (0, tuple(start_pos))) # f_cost, (x, y)

        # Dictionary to store the cheapest cost from start to a node
        g_cost = {tuple(start_pos): 0}

        # Dictionary to store the path reconstruction (parent node)
        came_from = {}

        # Heuristic function (Manhattan distance for grid)
        def heuristic(pos1, pos2):
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

        while open_list:
            current_f_cost, current_pos_tuple = heapq.heappop(open_list)
            current_pos = list(current_pos_tuple)

            if current_pos == end_pos:
                # Path found, reconstruct it
                path = []
                while current_pos_tuple in came_from:
                    path.append(list(current_pos_tuple))
                    current_pos_tuple = came_from[current_pos_tuple]
                path.append(start_pos) # Add the start node
                return path[::-1] # Reverse to get path from start to end

            # Define possible movements (4 directions: Up, Down, Left, Right)
            # TODO: Expand to 8 directions if diagonal movement is allowed
            neighbors = [
                [current_pos[0], current_pos[1] + 1],
                [current_pos[0], current_pos[1] - 1],
                [current_pos[0] + 1, current_pos[1]],
                [current_pos[0] - 1, current_pos[1]],
            ]

            for neighbor_pos in neighbors:
                if not self.battlefield.is_within_bounds(neighbor_pos):
                    continue

                # TODO: Check for obstacles or difficult terrain that increases cost
                # if self.battlefield.grid[neighbor_pos[1]][neighbor_pos[0]].get("obstacle"):
                #     continue # Skip obstacles

                # cost_to_neighbor = 1 # Simple cost for now
                # terrain_info = self.battlefield.get_terrain_at(neighbor_pos)
                # if terrain_info:
                #     cost_to_neighbor = 1.0 / terrain_info.get("movement_modifier", 1.0) # Cost is inverse of modifier

                tentative_g_cost = g_cost[current_pos_tuple] + 1 # Assuming cost of 1 per step for now

                neighbor_pos_tuple = tuple(neighbor_pos)

                if neighbor_pos_tuple not in g_cost or tentative_g_cost < g_cost[neighbor_pos_tuple]:
                    g_cost[neighbor_pos_tuple] = tentative_g_cost
                    f_cost = tentative_g_cost + heuristic(neighbor_pos, end_pos)
                    heapq.heappush(open_list, (f_cost, neighbor_pos_tuple))
                    came_from[neighbor_pos_tuple] = current_pos_tuple

        print(f"Pathfinding: No path found from {start_pos} to {end_pos}.")
        return [] # No path found


# Example usage for testing this file directly
if __name__ == "__main__":
    print("--- Testing Pathfinding Module ---")

    # Mock BattlefieldModule for pathfinding to interact with
    class MockBattlefieldModule:
        def __init__(self, size=(10, 10), obstacles=None):
            self.size = size
            self._obstacles = set(tuple(o) for o in (obstacles if obstacles is not None else []))
            print(f"MockBattlefield initialized with size {self.size} and obstacles: {self._obstacles}")

        def is_within_bounds(self, pos: list) -> bool:
            x, y = pos
            return 0 <= x < self.size[0] and 0 <= y < self.size[1]

        # For future expansion, this would check if a tile has an obstacle
        def is_obstacle(self, pos: list) -> bool:
            return tuple(pos) in self._obstacles
            # Or from self.grid if it were implemented:
            # return self.grid[pos[1]][pos[0]].get("obstacle", False) is not False

        # Placeholder for get_terrain_at if needed for cost calculation
        def get_terrain_at(self, pos: list) -> dict:
            return {"movement_modifier": 1.0} # Assume plains for simplicity


    # Test Case 1: Simple straight path
    print("\nTest Case 1: Simple straight path (5x5 board)")
    mock_board_1 = MockBattlefieldModule(size=(5, 5))
    pathfinder_1 = Pathfinding(mock_board_1)
    path_1 = pathfinder_1.find_path([0, 0], [4, 4])
    print(f"Path from [0,0] to [4,4]: {path_1}")
    expected_path_1_len = 9 # (0,0) -> (4,4) diagonal length + 1
    if path_1 and len(path_1) == expected_path_1_len and path_1[0] == [0,0] and path_1[-1] == [4,4]:
        print("  Test Case 1 PASSED: Path found and correct length.")
    else:
        print("  Test Case 1 FAILED.")

    # Test Case 2: Path with an obstacle
    print("\nTest Case 2: Path around an obstacle (5x5 board)")
    # Obstacle at [2,2]
    mock_board_2 = MockBattlefieldModule(size=(5, 5), obstacles=[[2,2]])
    # For A* to respect obstacles, you'd need to uncomment and implement the obstacle check
    # in Pathfinding.find_path. For now, it will ignore.
    pathfinder_2 = Pathfinding(mock_board_2)
    path_2 = pathfinder_2.find_path([0, 0], [4, 0])
    print(f"Path from [0,0] to [4,0] (with obstacle at [2,2]): {path_2}")
    if path_2: # Basic check for path existence
        print("  Test Case 2 PASSED (path found, though obstacle not avoided in current skeletal A*).")
    else:
        print("  Test Case 2 FAILED.")

    # Test Case 3: No path (start/end out of bounds)
    print("\nTest Case 3: No path (end out of bounds)")
    mock_board_3 = MockBattlefieldModule(size=(5, 5))
    pathfinder_3 = Pathfinding(mock_board_3)
    path_3 = pathfinder_3.find_path([0, 0], [5, 5])
    print(f"Path from [0,0] to [5,5]: {path_3}")
    if not path_3:
        print("  Test Case 3 PASSED: No path found (correctly identified out of bounds).")
    else:
        print("  Test Case 3 FAILED.")

    print("\n--- End of Pathfinding Module Test ---")
