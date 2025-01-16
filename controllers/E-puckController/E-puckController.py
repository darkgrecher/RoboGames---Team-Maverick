from controller import Robot, DistanceSensor
import math

# Constants for wheel and robot dimensions
WHEEL_RADIUS = 0.02  
WHEEL_DISTANCE = 0.052 

# Initial position of the e-puck robot
INITIAL_X = 0.375
INITIAL_Y = -0.875

# Constraints with respect to the origin (0, 0)
X_MIN = 18
X_MAX = 20
Y_MIN = -5
Y_MAX = 2

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
    
    # Perform simulation steps until Webots is stopping the controller
    while robot.step(timestep) != -1:
        
        # Calculate current robot position
        delta_x, delta_y = get_robot_position(left_encoder, right_encoder)
        current_x = INITIAL_X + delta_x
        current_y = INITIAL_Y + delta_y
        
        # Debugging output
        print(f"Current Position: ({current_x:.3f}, {current_y:.3f})")
        
        # Check if the robot is within the specified region
        if X_MIN < current_x < X_MAX and Y_MIN < current_y < Y_MAX:
            # Pause the robot
            left_motor.setVelocity(0)
            right_motor.setVelocity(0)
            print("Robot paused in the specified region.")
            continue  # Skip the rest of the loop
        
        prox_sensors = []
        for ind in range(8):
            sensor_name = 'ps' + str(ind)
            prox_sensors.append(robot.getDevice(sensor_name))
            prox_sensors[ind].enable(timestep)
        
        left_wall = prox_sensors[5].getValue() > 80
        front_wall = prox_sensors[7].getValue() > 80
        
        left_speed = max_speed
        right_speed = max_speed
        
        if front_wall:
            print('Turn right in place')
            left_speed = max_speed
            right_speed = -max_speed
            
        else:
            if left_wall:
                print("Drive forward")
                left_speed = max_speed
                right_speed = max_speed
            else:
                print("Turn right")
                left_speed = max_speed / 8
                right_speed = max_speed
                
        
        # Set motor velocities
        left_motor.setVelocity(left_speed)
        right_motor.setVelocity(right_speed)

if __name__ == "__main__":
    my_robot = Robot()
    run_robot(my_robot)