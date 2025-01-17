from controller import Robot, DistanceSensor, Camera
import math

# Constants for wheel and robot dimensions
WHEEL_RADIUS = 0.02  # in meters
WHEEL_DISTANCE = 0.052  # in meters

# Initial position of the e-puck robot
INITIAL_X = 0.375
INITIAL_Y = -0.875

# Constraints with respect to the origin (0, 0)
X_MIN = 18
X_MAX = 20
Y_MIN = -5
Y_MAX = 2

# Constants for camera and color detection
TIME_STEP = 64  # Time step in milliseconds
COLOR_TOLERANCE = 50  # Tolerance for color matching

# Define RGB ranges for colors (Red, Yellow, Pink, Brown, Green)
COLORS = {
    "Red": (255, 0, 0),
    "Yellow": (255, 255, 0),
    "Pink": (255, 0, 255),
    "Brown": (165, 105, 30),
    "Green": (0, 255, 0),
}

def get_robot_position(left_encoder, right_encoder):
    # Calculate the distance each wheel has traveled
    left_distance = left_encoder.getValue() * WHEEL_RADIUS
    right_distance = right_encoder.getValue() * WHEEL_RADIUS

    # Calculate the average distance traveled by the robot
    distance = (left_distance + right_distance) / 2.0

    # Calculate the robot's orientation (angle)
    theta = (right_distance - left_distance) / WHEEL_DISTANCE

    # Update the robot's position based on distance and orientation
    delta_x = distance * math.cos(theta)
    delta_y = distance * math.sin(theta)

    return delta_x, delta_y

def match_color(pixel, target_color):
    r, g, b = pixel
    tr, tg, tb = target_color
    return abs(r - tr) < COLOR_TOLERANCE and abs(g - tg) < COLOR_TOLERANCE and abs(b - tb) < COLOR_TOLERANCE

def run_robot(robot):
    timestep = int(robot.getBasicTimeStep())
    max_speed = 6.28

    # Motor devices
    left_motor = robot.getDevice('left wheel motor')
    right_motor = robot.getDevice('right wheel motor')
    left_motor.setPosition(float('inf'))
    right_motor.setPosition(float('inf'))

    # Encoder devices
    left_encoder = robot.getDevice('left wheel sensor')
    right_encoder = robot.getDevice('right wheel sensor')
    left_encoder.enable(timestep)
    right_encoder.enable(timestep)

    # Proximity sensors
    prox_sensors = []
    for ind in range(8):
        sensor_name = f'ps{ind}'
        prox_sensors.append(robot.getDevice(sensor_name))
        prox_sensors[ind].enable(timestep)

    # Enable the camera
    camera = robot.getDevice("camera")
    camera.enable(timestep)

    # Initialize robot position
    current_x, current_y = INITIAL_X, INITIAL_Y

    # Main loop
    while robot.step(timestep) != -1:
        # Update robot position
        delta_x, delta_y = get_robot_position(left_encoder, right_encoder)
        current_x = INITIAL_X + delta_x
        current_y = INITIAL_Y + delta_y

        # Debugging output
        print(f"Current Position: ({current_x:.3f}, {current_y:.3f})")

        # Get the image from the camera
        image = camera.getImage()
        width, height = camera.getWidth(), camera.getHeight()

        # Process the image (check the center pixel for simplicity)
        x, y = width // 2, height // 2  # Center of the image
        r = camera.imageGetRed(image, width, x, y)
        g = camera.imageGetGreen(image, width, x, y)
        b = camera.imageGetBlue(image, width, x, y)

        # Check if the color matches any of the predefined colors
        detected_color = None
        for color_name, target_rgb in COLORS.items():
            if match_color((r, g, b), target_rgb):
                detected_color = color_name
                break

        if detected_color:
            print(f"Detected Color: {detected_color}")

        # Navigation logic
        left_wall = prox_sensors[1].getValue() > 80
        front_wall = prox_sensors[7].getValue() > 80

        left_speed = max_speed
        right_speed = max_speed

        if front_wall:
            left_speed = max_speed
            right_speed = -max_speed
        else:
            if left_wall:
                left_speed = max_speed
                right_speed = max_speed
            else:
                left_speed = max_speed / 4
                right_speed = max_speed

            left_corner = prox_sensors[0].getValue() > 80
            right_wall = prox_sensors[2].getValue() > 80

            if left_corner or right_wall:
                left_speed = max_speed
                right_speed = max_speed / 4

        left_motor.setVelocity(right_speed)
        right_motor.setVelocity(left_speed)

if __name__ == "__main__":
    my_robot = Robot()  # Create an instance of the Robot class
    run_robot(my_robot)  # Run the main function
