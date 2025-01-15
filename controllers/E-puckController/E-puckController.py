from controller import Robot

# Constants
TIME_STEP = 64
MAX_SPEED = 6.28
THRESHOLD = 80  # Laser sensor threshold for detecting a wall
RECOVERY_THRESHOLD = 50  # Threshold for detecting a wall loss
LASER_SENSOR_RANGE = 100  # Increased range for laser sensors

# Initialize the robot
robot = Robot()

# Enable laser sensors
laser_sensors = []
for i in range(8):
    sensor = robot.getDevice(f'ls{i}')
    sensor.enable(TIME_STEP)
    sensor.setRange(LASER_SENSOR_RANGE)  # Set the increased range
    laser_sensors.append(sensor)

# Enable wheels
left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
left_motor.setPosition(float('inf'))  # Set velocity control mode
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# Wall-following logic
def follow_wall():
    lost_wall = False  # Track if the wall has been temporarily lost

    while robot.step(TIME_STEP) != -1:
        # Read laser sensor values
        sensor_values = [sensor.getValue() for sensor in laser_sensors]

        # Front, left, and right sensor values
        front_left = sensor_values[7]
        front_right = sensor_values[0]
        side_left = sensor_values[5]
        side_right = sensor_values[2]

        if front_left > THRESHOLD or front_right > THRESHOLD:
            # Wall in front - turn right
            left_motor.setVelocity(MAX_SPEED * 0.5)
            right_motor.setVelocity(-MAX_SPEED * 0.5)
            lost_wall = False
        elif side_left > THRESHOLD:
            # Wall on the left - move forward while keeping close to the wall
            left_motor.setVelocity(MAX_SPEED * 0.6)
            right_motor.setVelocity(MAX_SPEED * 0.4)
            lost_wall = False
        elif side_right > THRESHOLD:
            # Wall on the right - move forward while keeping close to the wall
            left_motor.setVelocity(MAX_SPEED * 0.4)
            right_motor.setVelocity(MAX_SPEED * 0.6)
            lost_wall = False
        else:
            # No wall detected - recover by turning in the direction of the last wall
            if lost_wall:
                # If the wall is lost, keep turning slowly to find it
                left_motor.setVelocity(MAX_SPEED * 0.3)
                right_motor.setVelocity(-MAX_SPEED * 0.3)
            else:
                # If the wall was just lost, turn slightly in the last direction
                lost_wall = True
                left_motor.setVelocity(MAX_SPEED * 0.5)
                right_motor.setVelocity(-MAX_SPEED * 0.5)

# Run the wall-following function
follow_wall()
