from controller import Robot, DistanceSensor, Camera
import math

# Constants for wheel and robot dimensions
WHEEL_RADIUS = 0.02  # in meters
WHEEL_DISTANCE = 0.052  # in meters

# Initial position of the e-puck robot
INITIAL_X = 0.375
INITIAL_Y = -0.875

# Constants for camera and color detection
TIME_STEP = 60 # Time step in milliseconds

# Define RGB ranges for colors with individual tolerances
COLORS = {
    "Red": {"rgb": (255, 0, 0), "tolerance": 100},  # Increase tolerance for red
    "Yellow": {"rgb": (255, 255, 0), "tolerance": 80},  # Increased tolerance for Yellow
    "Pink": {"rgb": (255, 0, 255), "tolerance": 150},  # Increased tolerance for Pink
    "Brown": {"rgb": (165, 105, 30), "tolerance": 100},  # Increased tolerance for Brown
    "Green": {"rgb": (0, 255, 0), "tolerance": 100},
}

COLOR_ARRAY = ["Red", "Yellow", "Pink", "Brown", "Green"]

# Define a threshold for proximity sensor values
PROX_SENSOR_THRESHOLD = 80

def euclidean_distance(color1, color2):
    """Calculate Euclidean distance between two RGB colors."""
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

def match_color(pixel, target_color, tolerance):
    """Check if the pixel color matches the target color within a tolerance."""
    distance = euclidean_distance(pixel, target_color)
    return distance < tolerance

def run_robot(robot):
    timestep = int(robot.getBasicTimeStep())
    max_speed = 6.28

    # Motor devices
    left_motor = robot.getDevice('left wheel motor')
    right_motor = robot.getDevice('right wheel motor')
    left_motor.setPosition(float('inf'))
    right_motor.setPosition(float('inf'))

    # Proximity sensors
    prox_sensors = []
    for ind in range(8):
        sensor_name = f'ps{ind}'
        prox_sensors.append(robot.getDevice(sensor_name))
        prox_sensors[ind].enable(timestep)

    # Enable the camera
    camera = robot.getDevice("camera")
    camera.enable(timestep)

    # To store the detected colors
    detected_colors = []
    printed_colors = set()  # Set to track printed colors

    # Variable to track if red color is detected
    red_detected = False

    # Main loop
    while robot.step(timestep) != -1:
        # Get the image from the camera
        image = camera.getImage()
        width, height = camera.getWidth(), camera.getHeight()

        # Process the image (check the center pixel for simplicity)
        x, y = width // 2, height // 2  # Center of the image
        r = camera.imageGetRed(image, width, x, y)
        g = camera.imageGetGreen(image, width, x, y)
        b = camera.imageGetBlue(image, width, x, y)

        # Skip normalization; compare raw RGB directly
        color = (r, g, b)

        # Check if the color matches any of the predefined colors
        detected_color = None
        for color_name, color_data in COLORS.items():
            target_rgb = color_data["rgb"]
            tolerance = color_data["tolerance"]
            if match_color(color, target_rgb, tolerance):
                detected_color = color_name
                break

        # Get values from the proximity sensors ps0 and ps7
        ps0_value = prox_sensors[0].getValue()
        ps7_value = prox_sensors[7].getValue()

        # Check if both ps0 and ps7 sensors are triggered
        if detected_color and ps0_value > PROX_SENSOR_THRESHOLD and ps7_value > PROX_SENSOR_THRESHOLD:
            # Print color only once
            if (detected_color not in printed_colors) and  red_detected:
                print(f"Detected Color: {detected_color}")
                printed_colors.add(detected_color)

            if not red_detected:
                # Only detect red first
                if detected_color == "Red":
                    print("Red detected. Ready to detect other colors.")
                    red_detected = True
                    detected_colors.append(detected_color)
            else:
                # After red is detected, add other colors only if not already added
                if detected_color not in detected_colors:
                    detected_colors.append(detected_color)

                    # Keep the list size to 5 (Red, Yellow, Pink, Brown, Green)
                    if len(detected_colors) > 5:
                        detected_colors.pop(0)

            # Check if the detected colors match the sequence
            if detected_colors == COLOR_ARRAY:
                print("Detected color sequence matched! TASK COMPLETED.")
                left_motor.setVelocity(0)
                right_motor.setVelocity(0)
                break  # Exit the loop to stop the robot

        # Wall following logic based on proximity sensors
        left_wall = prox_sensors[1].getValue() > 80
        front_wall = prox_sensors[7].getValue() > 80
        left_corner = prox_sensors[0].getValue() > 80
        right_wall = prox_sensors[5].getValue() > 80

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

            if left_corner:
                left_speed = max_speed
                right_speed = max_speed / 4
            
            if right_wall:
                left_speed = max_speed
                right_speed = max_speed / 4

        # Set the motor speeds based on wall following and color detection
        left_motor.setVelocity(right_speed)
        right_motor.setVelocity(left_speed)


if __name__ == "__main__":
    my_robot = Robot()  # Create an instance of the Robot class
    run_robot(my_robot)  # Run the main function
