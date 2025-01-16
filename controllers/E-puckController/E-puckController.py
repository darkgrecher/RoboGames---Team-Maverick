from controller import Robot

# Initialize the robot and timestep
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Initialize the light sensor
light_sensor = robot.getDevice('light sensor')  # Use the name of the light sensor
light_sensor.enable(timestep)

while robot.step(timestep) != -1:
    # Read the value from the light sensor
    light_value = light_sensor.getValue()

    # Debugging output
    print(f"Light Sensor Value: {light_value}")

    # Example logic for detecting red light
    if light_value > 0:
        print("Light detected!")
    else:
        print("No light detected.")

