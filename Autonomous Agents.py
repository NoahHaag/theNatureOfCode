import math
import random
import sys

import pygame
import vnoise

noise_scale = 0.1
vnoise_engine = vnoise.Noise(seed=random.randint(0, 100000))

# Initialize pygame
pygame.init()

# Setup canvas dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autonomous Agents")

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GRAY = (127, 127, 127)


class Vehicle():
    def __init__(self, x, y, m):
        self.position = pygame.Vector2(x, y)
        self.acceleration = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(0, 0)

        self.maxspeed = 5
        self.maxforce = 0.2
        self.mass = m

        self.r = 6
        self.angle = 0

    def apply_force(self, force):
        f = force / self.mass
        self.acceleration += f

    def seek(self, target):
        desired = target - self.position
        if desired.length() == 0:
            return

        slowing_radius = 100

        if desired.length() < slowing_radius:
            desired_speed = (desired.length() / slowing_radius) * self.maxspeed
        else:
            desired_speed = self.maxspeed

        desired = desired.normalize() * desired_speed

        steer = desired - self.velocity

        if steer.length() > self.maxforce:
            steer = steer.clamp_magnitude(self.maxforce)

        return steer

    def update(self):
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0
        if self.velocity.length() > 0:
            _, heading_angle = self.velocity.as_polar()
            self.angle = heading_angle

    def show(self, surface):
        # Sized dynamically using self.radius
        r = self.r

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
        """Wraps the elongated triangle smoothly around screen borders."""
        # Account for the extended nose/tail length of the triangle
        buffer = self.r * 2

        # Wrap horizontally (Left and Right edges)
        if self.position.x > WIDTH + buffer:
            self.position.x = -buffer
        elif self.position.x < -buffer:
            self.position.x = WIDTH + buffer

        # Wrap vertically (Top and Bottom edges)
        if self.position.y > HEIGHT + buffer:
            self.position.y = -buffer
        elif self.position.y < -buffer:
            self.position.y = HEIGHT + buffer

    def follow_flowfield(self, flowfield):
        """Looks up the flow vector at the current position and steers along it."""
        desired = flowfield.lookup(self.position)

        if desired.length() == 0:
            return

        desired = desired.normalize() * self.maxspeed

        steer = desired - self.velocity

        if steer.length() > self.maxforce:
            steer = steer.clamp_magnitude(self.maxforce)

        self.apply_force(steer)

    def get_normal_point(self, p, a, b):
        """Helper function to calculate the scalar projection point along a line segment."""
        ap = p - a
        ab = b - a

        # Scale the vector down to a pure directional unit vector
        ab = ab.normalize()

        # Project ap onto ab using the vector dot product
        # This tells us how far along line 'ab' the point 'p' falls
        dot_product = ap.dot(ab)

        # Keep the normal point constrained strictly between the start and end of the segment
        # (Prevents vehicles from tracking paths that haven't started or already ended)
        line_length = (b - a).length()
        dot_product = max(0, min(line_length, dot_product))

        # The final screen point is the start coordinate plus the scaled direction vector
        return a + (ab * dot_product)

    def follow_path(self, path):
        # 1. Predict future position
        if self.velocity.length() == 0:
            future = self.position.copy()
        else:
            future = self.velocity.normalize() * 25
            future += self.position

        target = None
        world_record = math.inf

        # 2. Loop through every segment in the complex path
        for i in range(len(path.points) - 1):
            a = path.points[i]
            b = path.points[i + 1]

            normal_point = self.get_normal_point(future, a, b)

            # Segment boundary override check
            min_x, max_x = min(a.x, b.x), max(a.x, b.x)
            min_y, max_y = min(a.y, b.y), max(a.y, b.y)

            if normal_point.x < min_x or normal_point.x > max_x or normal_point.y < min_y or normal_point.y > max_y:
                normal_point = b.copy()

            distance = future.distance_to(normal_point)

            # 3. Find the closest line segment
            if distance < world_record:
                world_record = distance

                # Look ahead along the active line segment direction
                ab_unit = (b - a).normalize() if (b - a).length() > 0 else pygame.Vector2(1, 0)
                target = normal_point + (ab_unit * 25)

        # 4. If the agent drifts outside the path radius, steer back toward the path target
        if world_record > path.radius and target is not None:
            self.seek(target)

    def separate(self, vehicles):
        desired_separation = self.r * 4
        sum_vector = pygame.Vector2(0, 0)
        count = 0

        for other in vehicles:
            d = self.position.distance_to(other.position)

            if self != other and d < desired_separation:
                diff = self.position - other.position

                if diff.length() > 0:
                    diff = diff.normalize()

                sum_vector += diff
                count += 1

        if count > 0:
            if sum_vector.length() > 0:
                desired = sum_vector.normalize() * self.maxspeed
            else:
                desired = pygame.Vector2(0, 0)

            steer = desired - self.velocity

            if steer.length() > self.maxforce:
                steer = steer.clamp_magnitude(self.maxforce)
            self.apply_force(steer)

    def align(self, vehicles):

        neighbor_distance = 100
        velocity_sum = pygame.Vector2(0, 0)
        count = 0

        for other in vehicles:
            d = self.position.distance_to(other.position)

            if (self != other) and (d < neighbor_distance):
                velocity_sum += other.velocity
                count += 1

        if count > 0:

            if velocity_sum.length() > 0:
                velocity_sum = velocity_sum.normalize() * self.maxspeed

            steer = velocity_sum - self.velocity

            if steer.length() > self.maxforce:
                steer = steer.normalize() * self.maxforce

            return steer
        else:
            return pygame.Vector2(0, 0)

    def cohesion(self, vehicles):
        neighbor_distance = 50
        position_sum = pygame.Vector2(0, 0)
        count = 0

        for other in vehicles:
            # Calculate distance between this boid and the other boid
            d = self.position.distance_to(other.position)

            # Ensure we don't check against ourselves and the boid is close enough
            if (self != other) and (d < neighbor_distance):
                position_sum += other.position  # Add up all the others' positions
                count += 1

        if count > 0:
            position_sum /= count  # Find the average position (center of mass)

            # Use the seek() function. The target to seek is the average position of your neighbors.
            return self.seek(position_sum)
        else:
            # If no close boids are found, the steering force is zero.
            return pygame.Vector2(0, 0)

    def flock(self, vehicles):
        alignment = self.align(vehicles)
        self.apply_force(alignment)
        cohesion = self.cohesion(vehicles)
        self.apply_force(cohesion)
        self.separate(vehicles)


    def run(self):
        self.flock(vehicles)
        self.check_edges()
        self.show(screen)
        self.update()


class Target():
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.acceleration = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(5, 0)

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
        """Wraps the elongated triangle smoothly around screen borders."""
        if self.position.x > WIDTH:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = WIDTH

        if self.position.y > HEIGHT:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = HEIGHT

    def run(self, force):
        self.check_edges()
        self.update()
        self.show(screen)
        self.apply_force(force)


class Flowfield():
    def __init__(self):
        self.resolution = 25
        self.cols = math.floor(WIDTH / self.resolution)
        self.rows = math.floor(HEIGHT / self.resolution)

        self.field = []

        for i in range(self.cols):
            # 1. Create a fresh row list for this specific column channel
            row_list = []

            for j in range(self.rows):
                noise_val = vnoise_engine.noise2(i * noise_scale, j * noise_scale)
                angle_rad = (noise_val + 1.0) * math.pi

                force_x = math.cos(angle_rad)
                force_y = math.sin(angle_rad)

                # 2. Add the independent Vector instance directly to the row list
                row_list.append(pygame.Vector2(force_x, force_y))

            # 3. Push the fully populated row into your main grid container matrix
            self.field.append(row_list)

    def lookup(self, position):
        """Looks up the flow vector at a given world position."""
        col_index = int(position.x / self.resolution)
        row_index = int(position.y / self.resolution)

        column = max(0, min(self.cols - 1, col_index))
        row = max(0, min(self.rows - 1, row_index))

        return self.field[column][row].copy()


class Path():
    def __init__(self):
        self.radius = 20

        self.points = []

        self.start = pygame.Vector2(0, HEIGHT / 3)
        self.end = pygame.Vector2(WIDTH, (2 * HEIGHT / 3))

    def add_point(self, x, y):
        path_point = pygame.Vector2(x, y)
        self.points.append(path_point)

    def show(self, surface):
        # Guard clause: You need at least 2 points to draw a connected line path
        if len(self.points) < 2:
            return

        # --- 1. Draw a thicker gray line for the path radius ---
        # Note: Pygame doesn't natively support semi-transparent thick strokes
        # on a main canvas directly with draw.lines, so we use a smooth solid gray (200, 200, 200)
        thickness = int(self.radius * 2)

        # Arguments: (surface, color, closed_bool, points_list, width)
        # Setting closed to False keeps the path open, exactly like endShape() without CLOSE
        pygame.draw.lines(surface, (200, 200, 200), False, self.points, thickness)

        pygame.draw.lines(surface, (0, 0, 0), False, self.points, 1)


# Clock to control frame rate
clock = pygame.time.Clock()

car = Vehicle(100, 100, 5)

target = Target(WIDTH / 2, HEIGHT / 2)

flowfield = Flowfield()

vehicles = []

track_path = Path()
track_path.add_point(0, 250)
track_path.add_point(200, 100)
track_path.add_point(400, 400)
track_path.add_point(600, 150)
track_path.add_point(WIDTH, 250)

for i in range(200):
    vehicles.append(Vehicle(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), 5))

# Main application loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Clear screen
    screen.fill(COLOR_WHITE)

    # track_path.show(screen)

    target.show(screen)

    for vehicle in vehicles:
        vehicle.follow_flowfield(flowfield)
        vehicle.separate(vehicles)
        vehicle.run()

    # Update the display and maintain frame rate
    pygame.display.flip()
    clock.tick(60)
