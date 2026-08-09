import os
import random
import string
import math
import time

population = []
mutation_rate = 0.01
population_size = 1000
target = "to be or not to be"


class DNA():
    def __init__(self, length):
        allowed_chars = string.ascii_letters + " "
        self.genes = [random.choice(allowed_chars) for _ in range(length)]
        self.fitness = 0

    def calculate_fitness(self, target):
        score = 0
        for i in range(len(self.genes)):
            if self.genes[i] == target[i]:
                score += 1

        self.fitness = (score / len(target)) ** 2

    def get_phrase(self):
        return "".join(self.genes)

    def crossover(self, partner):
        # Initialize a new child DNA instance
        child = DNA(len(self.genes))

        # Pick a random midpoint cut-off index
        midpoint = random.randint(0, len(self.genes) - 1)

        for i in range(len(self.genes)):
            if i < midpoint:
                child.genes[i] = self.genes[i]
            else:
                child.genes[i] = partner.genes[i]

        return child

    def mutate(self, mutation_rate):
        allowed_chars = string.ascii_letters + " "
        for i in range(len(self.genes)):
            # Generate a random float between 0.0 and 1.0
            if random.random() < mutation_rate:
                self.genes[i] = random.choice(allowed_chars)

    def draw(self):
        for phrase in population:
            phrase.calculateFitness(target)


# --- Initialize Population ---
population = [DNA(len(target)) for _ in range(population_size)]
generation = 0
found = False

# --- Main Evolution Loop ---
while not found:
    generation += 1

    # 1. Calculate fitness for everyone
    for individual in population:
        individual.calculate_fitness(target)

    # 2. Find stats to display (Best phrase, average fitness)
    best_individual = max(population, key=lambda ind: ind.fitness)
    avg_fitness = sum(ind.fitness for ind in population) / population_size

    # Check if we hit the goal
    if best_individual.get_phrase() == target:
        found = True

    # 3. Live Dashboard Display
    # Clear screen: 'cls' for Windows, 'clear' for Mac/Linux
    os.system('cls' if os.name == 'nt' else 'clear')

    print("=" * 40)
    print(f"GENETIC ALGORITHM STATUS (Gen: {generation})")
    print("=" * 40)
    print(f"Target Phrase:   '{target}'")
    print(f"Best Match:      '{best_individual.get_phrase()}'")
    print(f"Average Fitness: {avg_fitness:.4f}")
    print("-" * 40)
    print("Sample of Current Generation:")

    # Print the first 10 phrases just to show the pool working
    for ind in population[:10]:
        print(f"  {ind.get_phrase()}")
    print("=" * 40)

    if found:
        print("\n🎉 Target reached successfully!")
        break

    # Small artificial delay so human eyes can watch it evolve
    time.sleep(0.01)

    # 4. Selection (Build Mating Pool)
    mating_pool = []
    for individual in population:
        # Scale fitness to integers.
        # Multiplied by 1000 since squaring fitness makes numbers smaller.
        n = math.floor(individual.fitness * 1000)
        mating_pool.extend([individual] * n)

    # Safety check: If pool is empty (early generations), fill with current population
    if not mating_pool:
        mating_pool = population[:]

    # 5. Reproduction (Create next generation)
    next_population = []
    for _ in range(population_size):
        parent_a = random.choice(mating_pool)
        parent_b = random.choice(mating_pool)

        child = parent_a.crossover(parent_b)
        child.mutate(mutation_rate)
        next_population.append(child)

    population = next_population
