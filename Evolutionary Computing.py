import random
import string

population = []

class DNA():
    def __init__(self, length):
        self.genes = []
        for i in len(length):
            self.genes[i] = random.choice(string.ascii_letters)