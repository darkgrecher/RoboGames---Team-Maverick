from controller import Robot, Camera

# Create a Robot instance
robot = Robot()

# Constants
TIME_STEP = 64  # Time step in milliseconds
COLOR_TOLERANCE = 50  # Tolerance for color matching

# Enable the camera
camera = robot.getDevice("camera")  # Replace "camera" with your camera's name
camera.enable(TIME_STEP)

# Define RGB ranges for colors (Red, Yellow, Pink, Brown, Green)
colors = {
    "Red": (255, 0, 0),
    "Yellow": (255, 255, 0),
    "Pink": (255, 0, 255),
    "Brown": (165, 105, 30),
    "Green": (0, 255, 0),
}

# Function to match colors
def match_color(pixel, target_color):
    r, g, b = pixel
    tr, tg, tb = target_color
    return abs(r - tr) < COLOR_TOLERANCE and abs(g - tg) < COLOR_TOLERANCE and abs(b - tb) < COLOR_TOLERANCE

# Main loop
while robot.step(TIME_STEP) != -1:
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
    for color_name, target_rgb in colors.items():
        if match_color((r, g, b), target_rgb):
            detected_color = color_name
            break

    # Print the detected color
    if detected_color:
        print(f"Detected Color: {detected_color}")

    # Stop after detection (or continue if exploring the maze)
    # robot.step() will loop until you exit manually or add a stopping condition
