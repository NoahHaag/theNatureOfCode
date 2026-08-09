import math
import random
import sys

import pygame

# Initialize pygame
pygame.init()

# Setup canvas dimensions
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle System with repeller")

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (127, 127, 127)


class Particle():
    def __init__(self, x, y, m):
        self.position = pygame.Vector2(x, y)
        self.acceleration = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(random.uniform(-2, 2), 0)
        self.lifespan = 500

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

    def apply_force(self, force):
        """Apply a force as a pygame.Vector2 to all particles."""
        for particle in self.particles:
            particle.apply_force(force)

    def apply_repeller(self, repeller):
        """Calculate a force for each particle based on a repeller."""
        for particle in self.particles:
            force = repeller.repel(particle)
            particle.apply_force(force)

    def apply_attractor(self, attractor):
        for particle in self.particles:
            force = attractor.attract(particle)
            particle.apply_force(force)

    def run(self, force):
        self.add_particle()
        self.apply_force(force)
        for i in reversed(range(len(self.particles))):
            particle = self.particles[i]
            particle.run()
            if particle.is_Dead():
                self.particles.pop(i)


class Confetti(Particle):
    def __init__(self, x, y, m):
        super().__init__(x, y, m)
        self.color = ((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    def show(self, surface):
        angle_rad = (self.position.x / WIDTH) * (math.pi * 4)
        angle_deg = math.degrees(angle_rad)

        size = 12
        confetti_surf = pygame.Surface((size, size), pygame.SRCALPHA)

        current_alpha = max(0, min(255, self.lifespan))
        fill_color = (*self.color, current_alpha)

        pygame.draw.rect(confetti_surf, fill_color, (0, 0, size, size))
        pygame.draw.rect(confetti_surf, (0, 0, 0, current_alpha), (0, 0, size, size), 1)

        rotated_surf = pygame.transform.rotate(confetti_surf, angle_deg)
        new_rect = rotated_surf.get_rect(center=(self.position.x, self.position.y))
        surface.blit(rotated_surf, new_rect.topleft)


class Repeller():
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.power = 250
        self.radius = 50

    def show(self, surface):
        pygame.draw.circle(surface, "red", (self.position.x, self.position.y), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (self.position.x, self.position.y), self.radius, 1)

    def repel(self, particle):
        force = self.position - particle.position

        distance = force.length()

        if distance == 0:
            return pygame.Vector2(0, 0)

        distance = max(5, min(50, distance))

        strength = -1 * self.power / (distance * distance)

        force_direction = force.normalize()
        repel_force = force_direction * strength

        return repel_force

class Attractor():
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.power = 250
        self.radius = 50

    def show(self, surface):
        pygame.draw.circle(surface, "green", (self.position.x, self.position.y), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (self.position.x, self.position.y), self.radius, 1)

    def attract(self, particle):
        force = self.position + particle.position

        distance = force.length()

        if distance == 0:
            return pygame.Vector2(0, 0)

        distance = max(5, min(50, distance))

        strength = self.power / (distance * distance)

        force_direction = force.normalize()
        attract_force = force_direction * strength

        return attract_force


# Clock to control frame rate
clock = pygame.time.Clock()

particles = []
emitter = Emitter(WIDTH / 2, 20)
repeller = Repeller(0, 250)
attractor = Attractor(WIDTH, 250)

gravity = pygame.Vector2(0, 0.5)
# Main application loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Clear screen
    screen.fill(COLOR_WHITE)

    emitter.apply_repeller(repeller)
    emitter.apply_attractor(attractor)
    emitter.run(gravity)

    # Render the repeller boundary obstacle
    repeller.show(screen)
    attractor.show(screen)

    # Update the display and maintain frame rate
    pygame.display.flip()
    clock.tick(60)
