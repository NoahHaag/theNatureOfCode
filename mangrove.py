import math
import random
import sys

import pygame

# Initialize pygame
pygame.init()

# Setup canvas dimensions
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle System")

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (127, 127, 127)


class Particle():
    def __init__(self, x, y, m):
        self.position = pygame.Vector2(x, y)
        self.acceleration = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(random.uniform(-2, 2), 0)
        self.lifespan = 255

        self.mass = m
        self.radius = self.mass * 4
        self.bounce = 0.9

    def apply_force(self, force):
        f = force / self.mass
        self.acceleration += f

    def update(self):
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0
        self.lifespan = max(0, self.lifespan - 2)

    def show(self, surface):
        surf_size = self.radius * 2
        alpha_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)

        pygame.draw.circle(alpha_surf, (127, 127, 127), (self.radius, self.radius), self.radius)
        pygame.draw.circle(alpha_surf, (0, 0, 0), (self.radius, self.radius), self.radius, 1)

        surface.blit(alpha_surf, self.position - pygame.Vector2(self.radius, self.radius))

    def is_Dead(self):
        return self.lifespan <= 0

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

    def run(self):
        self.check_edges()
        self.show(screen)
        self.update()


class Emitter():
    def __init__(self, x, y):
        self.particles = []
        self.origin = pygame.Vector2(x, y)

    def add_particle(self):
        self.particles.append(Particle(self.origin.x, self.origin.y, 5))

    def run(self):
        self.add_particle()
        for i in reversed(range(len(self.particles))):
            particle = self.particles[i]
            particle.apply_force(current)
            particle.run()
            if particle.is_Dead():
                self.particles.pop(i)


# Clock to control frame rate
clock = pygame.time.Clock()

particles = []
emitter = Emitter(0, 250)

# Main application loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Clear screen
    screen.fill(COLOR_WHITE)

    current = pygame.Vector2(random.uniform(0,1), random.uniform(-2,2))

    emitter.run()

    # Update the display and maintain frame rate
    pygame.display.flip()
    clock.tick(60)
