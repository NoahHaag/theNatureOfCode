import turtle
import random
import time

import vnoise


WIDTH = 600
HEIGHT = 600


screen = turtle.Screen()
screen.setup(width=WIDTH, height=HEIGHT)
screen.tracer(0.5)

zoom_factor = 200
screen.setworldcoordinates(-zoom_factor, -zoom_factor, zoom_factor, zoom_factor)


pen = turtle.Turtle()
pen.speed(0)

nv = vnoise.Noise()



class Walker:
    def __init__(self, sc):
        self.tx = random.randint(-10000,10000)
        self.ty = random.randint(-10000,10000)
        self.x = 0
        self.y = 0

    def draw(self, pen, color = "black"):
        # set color (equivalent to stroke(0) for black)
        pen.pencolor(color)
        pen.penup()
        pen.goto(self.x, self.y)
        pen.pendown()
        pen.dot(4)  # 4 is the diameter of the dot in pixels

    def step_gauss(self):
        xstep = random.gauss(0,1)
        ystep = random.gauss(0,1)

        self.x += xstep
        self.y += ystep

    def step_random(self):
        # Randomly choose a direction
        choice = random.choice(range(4))
        if choice == 0:
            self.x += 1
        elif choice == 1:
            self.x -= 1
        elif choice == 2:
            self.y += 1
        else:
            self.y -= 1

    def big_stepper(self):
        choice = random.uniform(0,1)
        if choice < 0.01:
            xstep = random.uniform(-100, 100)
            ystep = random.uniform(-100, 100)
            self.x += xstep
            self.y += ystep
        else:
            xstep = random.uniform(-1, 1)
            ystep = random.uniform(-1, 1)
            self.x += xstep
            self.y += ystep

    def perlin_step(self):
        # 1. Get noise values between -0.5 and 0.5
        noise_x = nv.noise1(self.tx * 0.01)
        noise_y = nv.noise1(self.ty * 0.5)

        self.x += (noise_x * 4)
        self.y += (noise_y * 4)

        # 3. Increment time steps
        self.tx += 0.01
        self.ty += 0.01





pen.hideturtle()  # Hides the turtle icon so you only see the drawings
pen.speed(0)  # Sets drawing speed to the fastest setting

# 2. Instantiate your walker, passing the screen object
walker1 = Walker(screen)
walker2 = Walker(screen)
walker3 = Walker(screen)
walker4 = Walker(screen)

running = True
while running:
    try:
        walker1.perlin_step()
        walker1.draw(pen, "red")
        walker2.perlin_step()
        walker2.draw(pen, "blue")
        walker3.perlin_step()
        walker3.draw(pen, "green")
        walker4.perlin_step()
        walker4.draw(pen, "brown")


        screen.update()  # Refresh the screen to display the drawing
        time.sleep(0.005)  # Tiny pause to prevent freezing and control animation speed
    except turtle.Terminator:
        # Gracefully handle the user closing the window manually
        running = False

# Keep the window open
screen.exitonclick()
