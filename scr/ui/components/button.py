# real_time_chess/src/ui/components/button.py

# This module provides a basic Button component for the game's UI.
# For this skeletal version, it simulates button drawing and click detection
# using print statements. In a full graphical application, this would
# interact with a rendering library like Pygame or a web framework.

class Button:
    """
    A simple UI button component.
    """
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 color: tuple = (100, 100, 100), text_color: tuple = (255, 255, 255)):
        """
        Initializes a new Button.

        Args:
            x (int): The X-coordinate of the button's top-left corner.
            y (int): The Y-coordinate of the button's top-left corner.
            width (int): The width of the button.
            height (int): The height of the button.
            text (str): The text displayed on the button.
            color (tuple): RGB tuple for the button's background color.
            text_color (tuple): RGB tuple for the button's text color.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.text_color = text_color
        print(f"Button '{self.text}' created at ({x},{y}) with size {width}x{height}.")

    def draw(self):
        """
        Simulates drawing the button on the screen.
        In a graphical environment, this would use drawing functions from the UI library.
        """
        print(f"  [Button: '{self.text}' at ({self.x},{self.y}) - Drawing]")
        # In a real game with Pygame, this might look like:
        # pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # text_surface = font.render(self.text, True, self.text_color)
        # screen.blit(text_surface, (self.x + (self.width - text_surface.get_width()) // 2,
        #                            self.y + (self.height - text_surface.get_height()) // 2))

    def is_clicked(self, mouse_x: int, mouse_y: int) -> bool:
        """
        Checks if a given mouse click coordinate is within the button's bounds.

        Args:
            mouse_x (int): The X-coordinate of the mouse click.
            mouse_y (int): The Y-coordinate of the mouse click.

        Returns:
            bool: True if the click is within the button, False otherwise.
        """
        if self.x <= mouse_x <= self.x + self.width and \
           self.y <= mouse_y <= self.y + self.height:
            print(f"  [Button: '{self.text}' clicked at ({mouse_x},{mouse_y})]")
            return True
        return False

# Example usage for testing this file directly
if __name__ == "__main__":
    print("--- Testing Button Component ---")

    # Create a test button
    my_button = Button(x=100, y=50, width=150, height=40, text="Start Game")

    # Simulate drawing the button
    print("\nSimulating button drawing:")
    my_button.draw()

    # Simulate mouse clicks
    print("\nSimulating mouse clicks:")

    # Click inside the button
    print("Click at (120, 60):")
    if my_button.is_clicked(120, 60):
        print("  Button 'Start Game' was successfully clicked!")
    else:
        print("  Click missed the button.")

    # Click outside the button (below)
    print("\nClick at (120, 100):")
    if my_button.is_clicked(120, 100):
        print("  Button 'Start Game' was successfully clicked!")
    else:
        print("  Click missed the button.")

    # Click outside the button (to the right)
    print("\nClick at (300, 60):")
    if my_button.is_clicked(300, 60):
        print("  Button 'Start Game' was successfully clicked!")
    else:
        print("  Click missed the button.")

    print("\n--- End of Button Component Test ---")
