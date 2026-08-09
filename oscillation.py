import math
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

        self.angle = 0
        self.angleVelocity = 0
        self.angleAcceleration = 0

    def apply_force(self, force):
        f = force / self.mass
        self.acceleration += f

    def update(self):
        self.angleAcceleration = self.acceleration.x / self.radius
        self.velocity += self.acceleration
        self.position += self.velocity

        self.acceleration *= 0

        self.angleVelocity += self.angleAcceleration
        self.angle += self.angleVelocity

    def show(self, surface):
        # Draws the object onto the provided window surface
        pygame.draw.circle(surface, COLOR_GRAY, self.position, self.radius)
        pygame.draw.circle(surface, COLOR_BLACK, self.position, self.radius, 1)

        end_x = self.position.x + self.radius * math.cos(self.angle)
        end_y = self.position.y + self.radius * math.sin(self.angle)
        line_end = pygame.Vector2(end_x, end_y)

        # Draw the indicator line from center to edge
        pygame.draw.line(surface, 'red', self.position, line_end, 2)

    def check_edges(self):
        # Handle horizontal bouncing (Left and Right walls)
        if self.position.x + self.radius > WIDTH:
            self.position.x = WIDTH - self.radius
            self.velocity.x *= -1 * self.bounce
            self.angleVelocity *= -self.bounce
        elif self.position.x - self.radius < 0:
            self.position.x = self.radius
            self.velocity.x *= -1 * self.bounce
            self.angleVelocity *= -self.bounce

        # Handle vertical bouncing (Floor and Ceiling boundaries)
        if self.position.y + self.radius > HEIGHT:
            self.position.y = HEIGHT - self.radius
            self.velocity.y *= -1 * self.bounce
        elif self.position.y - self.radius < 0:
            self.position.y = self.radius
            self.velocity.y *= -1 * self.bounce


class Oscillator():
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)

        self.angle = pygame.Vector2(0, 0)
        self.angleVelocity = pygame.Vector2(random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05))
        self.amplitude = pygame.Vector2(random.uniform(20, WIDTH / 2), random.uniform(20, WIDTH / 2))

        self.radius = 25

    def update(self):
        self.angle += self.angleVelocity

    def show(self, surface):
        x = math.sin(self.angle.x) * self.amplitude.x
        y = math.sin(self.angle.y) * self.amplitude.y

        current_ball_position = pygame.Vector2(
            self.position.x + x,
            self.position.y + y
        )

        pygame.draw.circle(surface, COLOR_GRAY, current_ball_position, self.radius)
        pygame.draw.circle(surface, COLOR_BLACK, current_ball_position, self.radius, 1)
        pygame.draw.line(surface, COLOR_BLACK, self.position, current_ball_position)


# Clock to control frame rate
clock = pygame.time.Clock()
oscillator = []
for i in range(10):
    oscillator.append(Oscillator(WIDTH / 2, HEIGHT / 2))

# Main application loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    # Clear screen
    screen.fill(COLOR_WHITE)


    for i in range(len(oscillator)):
        oscillator[i].update()
        oscillator[i].show(screen)

    # Update the display and maintain frame rate
    pygame.display.flip()
    clock.tick(60)
