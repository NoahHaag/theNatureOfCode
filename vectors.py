import sys
import pygame
import random

# Initialize pygame
pygame.init()

# Setup canvas dimensions
WIDTH, HEIGHT = 640, 240
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("OOP Vector Motion with Acceleration")

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (127, 127, 127)


class Mover:
    def __init__(self):
        # In Python, instance variables are declared using 'self.'
        self.position = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        self.velocity = pygame.Vector2(0, 0)

        # Acceleration is the key!
        self.acceleration = pygame.Vector2(-0.001, 0.01)

        # The variable top_speed will limit the magnitude of velocity.
        self.top_speed = 10.0

        # Ball size settings
        self.radius = 24

    def update(self):
        # 1. Update acceleration in-place (Magnitude 0.5, random angle)
        self.acceleration.from_polar((0.5, random.uniform(0, 360)))

        # 2. Velocity changes by acceleration
        self.velocity += self.acceleration

        # 3. Limit the velocity by top_speed
        if self.velocity.length() > self.top_speed:
            self.velocity = self.velocity.clamp_magnitude(self.top_speed)

        # 4. Position changes by velocity
        self.position += self.velocity

    def show(self, surface):
        # Draws the object onto the provided window surface
        pygame.draw.circle(surface, COLOR_GRAY, self.position, self.radius)
        pygame.draw.circle(surface, COLOR_BLACK, self.position, self.radius, 1)

    def check_edges(self):
        # Wraps the position to the opposite side of the screen
        if self.position.x > WIDTH:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = WIDTH

        if self.position.y > HEIGHT:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = HEIGHT



# --- Program Execution Setup ---

# Instantiate the Mover object
mover = Mover()

# Clock to control frame rate
clock = pygame.time.Clock()

# Main application loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Clear screen
    screen.fill(COLOR_WHITE)

    # Call the Mover object's methods
    mover.update()
    mover.check_edges()
    mover.show(screen)

    # Update the display and maintain frame rate
    pygame.display.flip()
    clock.tick(60)
