import sys

import pygame

# Initialize pygame
pygame.init()

# Setup canvas dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cellular Automata")

cells = [1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0]

# Main application loopd
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Clear screen
    screen.fill((255, 255, 255))

    # Loop through every cell using its index and value
    for i, cell_state in enumerate(cells):
        # Create a fill based on its state (0 or 1).
        if cell_state == 0:
            fill_color = (255, 255, 255)  # White
        else:
            fill_color = (0, 0, 0)  # Black

        stroke_color = (0, 0, 0)  # Black

        # Define the rectangle dimensions (x, y, width, height)
        rect_coords = (i * 50, 0, 50, 50)

        # Draw the filled rectangle
        pygame.draw.rect(screen, fill_color, rect_coords)

        # Draw the cell outline (stroke) by adding thickness=1 as the last argument
        pygame.draw.rect(screen, stroke_color, rect_coords, 1)


    # Update the display and maintain frame rate
    pygame.display.flip()
    clock.tick(60)
