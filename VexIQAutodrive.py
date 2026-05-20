# My VEX IQ robot - drives in a square and stops if it sees stuff!!
# Making it autonomous with a bumper and distance sensor, no gyro needed.
# # Press the touchled to start it 

from vex import *
import math

brain = Brain()

# my motors and sensors
left_motor  = Motor(Ports.PORT1, False)
right_motor = Motor(Ports.PORT6, True)   # this one is backwards
touchled    = Touchled(Ports.PORT3)
bumper      = Bumper(Ports.PORT5)
my_distance = Distance(Ports.PORT2)

# robot size 
WHEEL_SIZE = 63.5   # mm, the wheels are 2.5 inches
ROBOT_WIDTH = 200   # mm between the wheels

# how fast and how far
SPEED = 60
TURN_SPEED = 35     # slower so the turns are nicer
SIDE = 300          # how long one side of the square is in mm

# when to stop because something is in the way
TOO_CLOSE = 150     # mm
GO_BACK = 120
TURN_AWAY = 60      # turn this much after backing up

#how many motor degrees = 1 mm
DEG_PER_MM = 360 / (math.pi * WHEEL_SIZE)


# IQ distance sensor returns a big number (or 0) when nothing is there.
# anything between 1mm and 1000mm is a real object.
MAX_VALID_MM = 1000


def read_distance():
    # returns mm if something real is in front, else -1
    d = my_distance.object_distance(MM)
    if d is None:
        return -1
    if d <= 0 or d > MAX_VALID_MM:
        return -1
    return int(d)


def show_distance():
    # put the distance on the screen
    d = read_distance()
    brain.screen.set_cursor(2, 1)
    brain.screen.clear_row(2)
    brain.screen.print("dist=", d, " mm")


def is_something_in_the_way():
    # check the bumper first (instant)
    if bumper.pressing():
        return True
    # then check the distance sensor
    d = read_distance()
    if d > 0 and d < TOO_CLOSE:
        return True
    return False


def stop_both():
    left_motor.stop()
    right_motor.stop()


def go_backward(mm):
    motor_deg = mm * DEG_PER_MM
    left_motor.spin_for(REVERSE, motor_deg, DEGREES, SPEED, PERCENT, False)
    right_motor.spin_for(REVERSE, motor_deg, DEGREES, SPEED, PERCENT, True)


def turn_right(deg):
    # the wheels go in opposite directions to spin the robot
    arc = (deg / 360) * math.pi * ROBOT_WIDTH    # how far each wheel goes
    motor_deg = arc * DEG_PER_MM
    left_motor.spin_for(FORWARD, motor_deg, DEGREES, TURN_SPEED, PERCENT, False)
    right_motor.spin_for(REVERSE, motor_deg, DEGREES, TURN_SPEED, PERCENT, True)


def turn_left(deg):
    arc = (deg / 360) * math.pi * ROBOT_WIDTH
    motor_deg = arc * DEG_PER_MM
    left_motor.spin_for(REVERSE, motor_deg, DEGREES, TURN_SPEED, PERCENT, False)
    right_motor.spin_for(FORWARD, motor_deg, DEGREES, TURN_SPEED, PERCENT, True)


def go_forward(mm):
    # drive forward but stop if we bump into something
    left_motor.set_position(0, DEGREES)
    target = mm * DEG_PER_MM

    left_motor.spin(FORWARD, SPEED, PERCENT)
    right_motor.spin(FORWARD, SPEED, PERCENT)

    while abs(left_motor.position(DEGREES)) < target:
        show_distance()
        if is_something_in_the_way():
            stop_both()
            brain.screen.set_cursor(3, 1)
            brain.screen.clear_row(3)
            brain.screen.print("Oh no something is there!")
            go_backward(GO_BACK)
            turn_right(TURN_AWAY)
            return False    # we didn't make it the whole way
        wait(20, MSEC)

    stop_both()
    return True


# don't start twice if I press the button by accident
already_running = False

def start():
    global already_running
    if already_running:
        return
    already_running = True

    brain.screen.clear_screen()
    brain.screen.print("GO!!")
    touchled.set_color(Color.GREEN)   # green = its running

    # do a square (4 sides + 4 right turns)
    for i in range(4):
        go_forward(SIDE)
        wait(0.2, SECONDS)
        turn_right(90)
        wait(0.2, SECONDS)

    brain.screen.set_cursor(3, 1)
    brain.screen.clear_row(3)
    brain.screen.print("All done :)")
    touchled.set_color(Color.BLUE)
    already_running = False


# get ready
brain.screen.clear_screen()
brain.screen.print("Press the LED to start!")
touchled.set_color(Color.BLUE)
touchled.pressed(start)

# keep showing the distance while we wait
while True:
    show_distance()
    wait(100, MSEC)