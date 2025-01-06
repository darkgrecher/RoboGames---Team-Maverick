from controller import Robot, Camera, Motor

# Time step
TIME_STEP = 64

# Initialize robot and devices
robot = Robot()
camera = robot.getDevice('camera')
camera.enable(TIME_STEP)
left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')

left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))

# Set initial velocity
left_motor.setVelocity(0)
right_motor.setVelocity(0)

# Color sequence
target_colors = ['red', 'yellow', 'pink', 'brown', 'green']
visited_colors = []

# Function to identify color from camera image
def detect_color(camera):
    image = camera.getImageArray()
    # Simplified detection logic (adjust thresholds as needed)
    red = sum([image[0][x][0] for x in range(len(image[0]))]) / len(image[0])
    green = sum([image[0][x][1] for x in range(len(image[0]))]) / len(image[0])
    blue = sum([image[0][x][2] for x in range(len(image[0]))]) / len(image[0])
    
    if red > green and red > blue:
        return 'red'
    elif green > red and green > blue:
        return 'green'
    elif blue > red and blue > green:
        return 'pink'  # Assuming high blue indicates pink
    # Add other color detections here
    return None

# Main loop
while robot.step(TIME_STEP) != -1:
    current_color = detect_color(camera)
    if current_color and current_color not in visited_colors:
        print(f"Detected {current_color}")
        if current_color == target_colors[len(visited_colors)]:
            visited_colors.append(current_color)
            print(f"Visited: {visited_colors}")
    
    if len(visited_colors) == len(target_colors):
        print("Task Complete!")
        break
    
    # Basic movement logic (adjust as needed for maze navigation)
    left_motor.setVelocity(2.0)
    right_motor.setVelocity(2.0)
