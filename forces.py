import sys
import pygame
import random

# Initialize pygame
pygame.init()

# Setup canvas dimensions
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("OOP Vector Motion with Acceleration")

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (127, 127, 127)


class Mover():
    def __init__(self, x, y, m):
        # In Python, instance variables are declared using 'self.'
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(-0.001, 0.01)
        self.top_speed = 10.0
        self.bounce = 0.9

        self.mass = m
        self.radius = self.mass * 8

    def apply_force(self, force):
        f = force / self.mass
        self.acceleration += f

    def update(self):
        self.velocity += self.acceleration
        # Position changes by velocity
        self.position += self.velocity
        # Reset acceleration to 0 for the next frame
        self.acceleration *= 0

    def show(self, surface):
        # Draws the object onto the provided window surface
        pygame.draw.circle(surface, COLOR_GRAY, self.position, self.radius)
        pygame.draw.circle(surface, COLOR_BLACK, self.position, self.radius, 1)

    def check_edges(self):
        # Handle horizontal bouncing (Left and Right walls)
        if self.position.x + self.radius > WIDTH:
            self.position.x = WIDTH - self.radius
            self.velocity.x *= -1 * self.bounce
        elif self.position.x - self.radius < 0:
            self.position.x = self.radius
            self.velocity.x *= -1 * self.bounce

        # Handle vertical bouncing (Floor and Ceiling boundaries)
        if self.position.y + self.radius > HEIGHT:
            self.position.y = HEIGHT - self.radius
            self.velocity.y *= -1 * self.bounce
        elif self.position.y - self.radius < 0:
            self.position.y = self.radius
            self.velocity.y *= -1 * self.bounce


class Liquid():
    def __init__(self, x, y, w, h, c):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.c = c  # coefficient of drag

    def show(self, surface):
        pygame.draw.rect(surface, 'cadetblue1', (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, "blue4", (self.x, self.y, self.w, self.h), 1)

    def contains(self, Mover):
        pos = Mover.position
        return (self.x < pos.x < self.x + self.w and
                self.y < pos.y < self.y + self.h)

    def calculate_drag(self, mover):
        speed = mover.velocity.length()
        if speed == 0:
            return pygame.Vector2(0, 0)
        drag_magnitude = self.c * speed * speed
        drag_direction = mover.velocity.normalize() * -1
        drag_force = drag_direction * drag_magnitude

        return drag_force


# --- Program Execution Setup ---

# Initialize the Mover objects
# mover1 = Mover(200, 50, 10)
# mover2 = Mover(50, 100, 1)
movers = []
for i in range(6):
    mass = random.uniform(0.5,10)
    x_spacing = 60 + i * 120
    movers.append(Mover(x_spacing, 50, mass))


# Initialise the Liquids
liquid1 = Liquid(0, HEIGHT / 2, WIDTH, HEIGHT / 2, 0.1)

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

    # Forces
    gravity = pygame.Vector2(0, 0.1)
    wind = pygame.Vector2(0.05, 0)

    # Call the Liquid objects
    liquid1.show(screen)

    for i in range(len(movers)):
        movers[i].apply_force(gravity * movers[i].mass)
        movers[i].update()
        movers[i].check_edges()
        movers[i].show(screen)
        if liquid1.contains(movers[i]):
            dragForce = liquid1.calculate_drag(movers[i])
            movers[i].apply_force(dragForce)


    # Update the display and maintain frame rate
    pygame.display.flip()
    clock.tick(60)
