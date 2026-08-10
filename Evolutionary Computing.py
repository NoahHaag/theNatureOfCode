import os
import random
import string
import math
import time
import pygame
import sys


# Initialize pygame
pygame.init()

# Setup canvas dimensions
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Rockets")

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (127, 127, 127)


class Rocket():
    def __init__(self, x, y, m):
        self.fitness = 0
        self.dna = DNA(250)
        self.geneCounter = 0
        self.hit_obstacle = False

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(-0.001, 0.01)
        self.top_speed = 10.0
        self.bounce = 0.9
        self.angle = 0.0

        self.mass = m
        self.radius = self.mass * 8

        self.hit_obstacle = False  # True if they touch a wall even once
        self.hit_target = False  # True if they reach the target radius
        self.collision_count = 0
        self.finish_time = 250  # Defaults to max lifespan if they never finish
        self.record_distance = 10000.0  # Set to a huge number initially

    def apply_force(self, force):
        f = force / self.mass
        self.acceleration += f

    def update(self, targets):  # <-- Must accept the targets parameter
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0

        if self.velocity.length() > 0:
            _, heading_angle = self.velocity.as_polar()
            self.angle = heading_angle
        self.check_edges()

        # Update the rocket's internal record_distance against the targets list...
        for target_obj in targets:
            d = self.position.distance_to(target_obj.position)
            if d < self.record_distance:
                self.record_distance = d
            if not self.hit_target and d < target_obj.radius:
                self.hit_target = True
                self.finish_time = self.geneCounter

    def show(self, surface):
        # Sized dynamically using self.radius
        r = self.radius

        # 1. Define the base points of a triangle pointing right (0 degrees)
        local_nose = pygame.Vector2(r * 2, 0)  # Tip pointing forward
        local_left = pygame.Vector2(-r, -r)  # Back left corner
        local_right = pygame.Vector2(-r, r)  # Back right corner

        # 2. Rotate the local points using the persistent self.angle updated by the physics step
        rotated_nose = local_nose.rotate(self.angle)
        rotated_left = local_left.rotate(self.angle)
        rotated_right = local_right.rotate(self.angle)

        # 3. Translate local offsets to world screen coordinates relative to self.position
        points = [
            self.position + rotated_nose,
            self.position + rotated_left,
            self.position + rotated_right
        ]

        # 4. Draw the clean steering triangle shape
        pygame.draw.polygon(surface, COLOR_GRAY, points)
        pygame.draw.polygon(surface, COLOR_BLACK, points, 1)

    def check_edges(self):
        """Bounces the triangle off the walls, reversing velocity on impact."""
        # Use the boid's radius as a buffer to bounce off the actual edge
        buffer = self.radius
        #
        # # Bounce horizontally (Left and Right edges)
        if self.position.x > WIDTH - buffer:
            self.position.x = WIDTH - buffer
            self.velocity.x *= -1  # Reverse horizontal direction
        elif self.position.x < buffer:
            self.position.x = buffer
            self.velocity.x *= -1  # Reverse horizontal direction
        #
        # Bounce vertically (Top and Bottom edges)
        if self.position.y > HEIGHT - buffer:
            self.position.y = HEIGHT - buffer
            self.velocity.y *= -1  # Reverse vertical direction
        elif self.position.y < buffer:
            self.position.y = buffer
            self.velocity.y *= -1  # Reverse vertical direction

        # buffer = self.radius * 2
        # # Wrap horizontally (Left and Right edges)
        # if self.position.x > WIDTH + buffer:
        #     self.position.x = -buffer
        # elif self.position.x < -buffer:
        #     self.position.x = WIDTH + buffer
        # Wrap vertically (Top and Bottom edges)
        # if self.position.y > HEIGHT + buffer:
        #     self.position.y = -buffer
        # elif self.position.y < -buffer:
        #     self.position.y = HEIGHT + buffer

    def calculate_fitness(self, targets):
        r_dist = max(self.record_distance, 1.0)
        f_time = max(self.finish_time, 1.0)

        # 1. Base Score
        self.fitness = 1 / (f_time * r_dist)
        self.fitness = self.fitness ** 4

        # 2. Cumulative Penalty: Every single bounce slices their score down
        # 0 bounces = 1.0x, 1 bounce = 0.1x, 2 bounces = 0.01x, 3 bounces = 0.001x!
        if self.hit_obstacle:
            penalty = 0.1 ** self.collision_count
            self.fitness *= penalty

        if self.hit_target:
            self.fitness *= 2.0

    def check_Obstacles(self, obstacles):
        if obstacles is None:
            return

        for obs in obstacles:
            if obs.contains(self.position):
                self.hit_obstacle = True
                self.collision_count += 1
                # Calculate how deep the rocket penetrated from each edge
                overlap_left   = self.position.x - obs.position.x
                overlap_right  = (obs.position.x + obs.width) - self.position.x
                overlap_top    = self.position.y - obs.position.y
                overlap_bottom = (obs.position.y + obs.height) - self.position.y

                # Find the smallest overlap to determine which side it impacted
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                # Reverse direction and push the rocket out based on the collision wall side
                if min_overlap == overlap_left:
                    self.position.x = obs.position.x
                    self.velocity.x *= -1 * self.bounce
                elif min_overlap == overlap_right:
                    self.position.x = obs.position.x + obs.width
                    self.velocity.x *= -1 * self.bounce
                elif min_overlap == overlap_top:
                    self.position.y = obs.position.y
                    self.velocity.y *= -1 * self.bounce
                elif min_overlap == overlap_bottom:
                    self.position.y = obs.position.y + obs.height
                    self.velocity.y *= -1 * self.bounce


    # FIX: Change the signature to accept both obstacles and targets
    def run(self, obstacles, targets):
        # 1. Apply genetic thruster forces
        self.apply_force(self.dna.genes[self.geneCounter])
        self.geneCounter += 1
        if self.geneCounter >= len(self.dna.genes):
            self.geneCounter = 0

        # 2. Process physics and target distance tracking
        # Make sure to pass the targets list into your update function here!
        self.update(targets)

        # 3. Handle obstacle collisions and bouncing
        self.check_Obstacles(obstacles)



class Target():
    def __init__(self, x, y, value):
        self.position = pygame.Vector2(x, y)
        self.acceleration = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(5, 0)
        self.value = 1

        self.radius = 25
        self.mass = 5

        self.maxspeed = 1.5
        self.maxforce = 0.2

    def show(self, surface):
        pygame.draw.circle(surface, COLOR_GRAY, self.position, self.radius)
        pygame.draw.circle(surface, COLOR_BLACK, self.position, self.radius, 1)

    def apply_force(self, force):
        f = force / self.mass
        self.acceleration += f

    def update(self):
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0

        if self.velocity.length() > self.maxspeed:
            self.velocity = self.velocity.clamp_magnitude(self.maxspeed)

    def check_edges(self):
        """Bounces the triangle off the walls, reversing velocity on impact."""
        # Use the boid's radius as a buffer to bounce off the actual edge
        buffer = self.r

        # Bounce horizontally (Left and Right edges)
        if self.position.x > WIDTH - buffer:
            self.position.x = WIDTH - buffer
            self.velocity.x *= -1  # Reverse horizontal direction
        elif self.position.x < buffer:
            self.position.x = buffer
            self.velocity.x *= -1  # Reverse horizontal direction

        # Bounce vertically (Top and Bottom edges)
        if self.position.y > HEIGHT - buffer:
            self.position.y = HEIGHT - buffer
            self.velocity.y *= -1  # Reverse vertical direction
        elif self.position.y < buffer:
            self.position.y = buffer
            self.velocity.y *= -1  # Reverse vertical direction


    def run(self, force):
        self.check_edges()
        self.update()
        self.show(screen)
        self.apply_force(force)


class DNA:
    def __init__(self, lifespan):
        # The genetic sequence is a list of vectors.
        self.genes = []

        # How strong can the thrusters be?
        self.max_force = 0.6

        # In Python, we pass lifespan into the constructor or use a global variable.
        for i in range(lifespan):
            # Create a random 2D unit vector (length of 1) facing a random direction
            random_vector = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))

            # Scale the vector randomly, but not stronger than the maximum force.
            random_force = random.uniform(0, self.max_force)
            random_vector *= random_force

            self.genes.append(random_vector)

    def crossover(self, partner):
        child = DNA(len(self.genes))
        midpoint = random.randint(0, len(self.genes) - 1)
        child.genes = self.genes[:midpoint] + partner.genes[midpoint:]
        return child

    def mutate(self, rate):
        for i in range(len(self.genes)):
            if random.random() < rate:
                random_vector = pygame.Vector2(1, 0).rotate(random.uniform(0, 360))
                self.genes[i] = random_vector * random.uniform(0, self.max_force)


class Population:
    # Population has variables to keep track of the mutation rate, current
    # population array, and number of generations.
    def __init__(self, mutation_rate, length):
        # Mutation rate
        self.mutation_rate = mutation_rate
        # Array to hold the current population
        self.population = []
        # Number of generations
        self.generations = 0

        for i in range(length):
            # Using standard list appending to add new Rockets
            self.population.append(Rocket(150, 450, 2))

    # Calculate the fitness for each rocket.
    # FIX: Change the signature to accept the targets list
    def fitness(self, targets):
        for rocket in self.population:
            rocket.calculate_fitness(targets)


    # The selection method normalizes all the fitness values.
    def weighted_selection(self):
        # Gather the normalized fitness values of all rockets
        weights = [rocket.fitness for rocket in self.population]

        # If total fitness is somehow 0, fallback to uniform random choice
        if sum(weights) == 0:
            return random.choice(self.population)

        # random.choices returns a list (e.g., [rocket]), so we extract the item at index 0
        selected_list = random.choices(self.population, weights=weights, k=1)
        return selected_list[0]

    def reproduction(self):
        new_population = []

        for i in range(len(self.population)):
            parent_a = self.weighted_selection()
            parent_b = self.weighted_selection()

            # FIX: Call crossover and mutate on the DNA attribute of the parents
            child_dna = parent_a.dna.crossover(parent_b.dna)
            child_dna.mutate(self.mutation_rate)

            # Create a new rocket with the new DNA sequence
            # (Note: Passing a mass of 2 to match your initial population setup)
            new_rocket = Rocket(150, 450, 2)
            new_rocket.dna = child_dna  # Inject the child DNA sequence

            new_population.append(new_rocket)

        self.population = new_population

    def live(self, obstacles, targets):  # <-- Update this line to accept targets
        for rocket in self.population:
            rocket.run(obstacles, targets)

    def show(self, surface):
        """Iterates through and renders every active rocket in the array."""
        for rocket in self.population:
            rocket.show(surface)



class Obstacle():
    def __init__(self, x, y, w, h):
        self.position = pygame.Vector2(x, y)
        self.width = w
        self.height = h
        self.rect = pygame.Rect(x, y, w, h)

    def show(self, surface):
        pygame.draw.rect(surface, COLOR_GRAY, (self.position.x, self.position.y, self.width, self.height))

    def contains(self, point):
        return (self.position.x <= point.x <= self.position.x + self.width
                and self.position.y <= point.y <= self.position.y + self.height)



# --- Program Execution Setup ---

# Position the target near the top of the screen
targets = [Target(650, 70, 10)]

lifespan = 400
lifecounter = 0

population = Population(0.05, 1000)
obstacles = [
    # Bottom Stair: Gap on the far right (width 150)
    Obstacle(0, 350, 650, 20),

    # Middle Stair: Gap shifted to the center-left (width 150)
    Obstacle(0, 240, 200, 20),
    Obstacle(350, 240, 450, 20),

    # Top Stair: Gap on the far left (width 150)
    Obstacle(150, 130, 650, 20)
]

# Clock to control frame rate
clock = pygame.time.Clock()

# --- Main Application Loop ---
while True:
    # 1. Handle Window Close Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 2. Run Generational Lifespan Timers and Physics Updates
    if lifecounter < lifespan:
        # Note: We now pass BOTH obstacles and targets down
        # so rockets can dynamically evaluate against your list of targets
        population.live(obstacles, targets)
        lifecounter += 1
    else:
        lifecounter = 0
        population.fitness(targets)  # Evaluate relative to multiple targets
        population.reproduction()
        population.generations += 1
        print(f"Generation spawned: {population.generations}")

    # 3. Clear Screen Frame Background
    screen.fill(COLOR_WHITE)

    # 4. Render All Static Environment Assets First
    for target in targets:
        target.show(screen)

    for obs in obstacles:
        obs.show(screen)

    # 5. FIX: Draw the rockets explicitly ON TOP of the clean canvas background
    # This prevents the screen wipe from instantly erasing them!
    population.show(screen)

    # 6. Maintain Display Frames and Refresh Game Canvas
    pygame.display.flip()
    clock.tick(240)

