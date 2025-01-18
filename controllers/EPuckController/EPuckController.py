"""
E-Puck Controller
"""

from controller import Robot, DistanceSensor, Compass, TouchSensor
from enum import Enum
import math
import os
import json

TIME_STEP = 64
MAX_SPEED = 6.28
DATA_FILENAME = os.getcwd() + '/data.json'

# --------------------------------------------------------------------

# Direction Class
class Direction(Enum):
    North = 'North'
    South = 'South'
    East = 'East'
    West = 'West'
    Left = 'Left'
    Right = 'Right'

# RobotState Class
class RobotState(Enum):
    FindWall = 'Find Wall'
    MountWall = 'Mount Wall'
    FollowWall = 'Follow Wall'
    TurnCorner = 'Turn Corner'
    CorrectTurn = 'CorrectTurn'
    GameOver = 'Game Over'

class HandRule(Enum):
    Left = "Left Hand Rule"
    Right = "Right Hand Rule"

# --------------------------------------------------------------------

class RunInfo:
    def __init__(self, count, robot):
        self.count = count
        self.state = robot.state
        self.bearing = robot.bearing
        self.direction = robot.direction
        self.left_wheel = robot.leftMotorSensor.getValue()
        self.right_wheel = robot.rightMotorSensor.getValue()

    def jsonData(self):
        return {
            "count": self.count,
            "state": self.state.name,
            "bearing": self.bearing,
            "direction": self.direction.name,
            "left_wheel": self.left_wheel,
            "right_wheel": self.right_wheel
        }

class MazeAttempt:
    def __init__(self, num):
        self.num = num
        self.rule = HandRule.Right
        self.info = {}
        self.info_count = 1

    def infoJsonData(self):
        info = {}
        for i in self.info:
            info[i] = self.info[i].jsonData()
        return info
    
    def jsonData(self):
        return {
            "num": self.num,
            "rule": self.rule.name,
            "info": self.infoJsonData()
        }

    def addInfo(self, robot):
        i = RunInfo(self.info_count, robot)
        self.info_count += 1
        self.info[str(i.count)] = i

    @staticmethod
    def Make(data):
        attempt = MazeAttempt(data['num'])
        if data['rule'] == 'Right':
            attempt.rule = HandRule.Right
        else:
            attempt.rule = HandRule.Left
        return attempt

class GameData:
    def __init__(self, robot):
        self.robot = robot
        self.data = {}
        self.current_attempt = MazeAttempt(int(len(self.data) + 1))
        self.readData()
        last_attempt = self.getLastAttempt()
        if last_attempt is not None:
            if last_attempt.rule == HandRule.Right:
                self.current_attempt.rule = HandRule.Left
            else:
                self.current_attempt.rule = HandRule.Right

    def readData(self):
        if os.path.isfile(DATA_FILENAME):
            with open(DATA_FILENAME, 'rt') as json_file:
                try:
                    self.data = json.load(json_file)
                except:
                    print("Unable to load JSON file:", DATA_FILENAME)

    def writeData(self):
        output_data = self.data
        output_data[str(self.current_attempt.num)] = self.current_attempt.jsonData()
        output_data = json.dumps(output_data, indent=4)
        f = open(DATA_FILENAME, 'wt')
        f.write(output_data)
        f.close()

    def parseFileData(self):
        if len(self.data) < 1:
            return
        self.attempt = len(self.data) + 1
        last_attempt = self.data[str(len(self.data))]
        if last_attempt['rule'] == 'Right':
            self.robot.hand_rule = HandRule.Left
        else:
            self.robot.hand_rule = HandRule.Right

    def getLastAttempt(self):
        if len(self.data) < 1:
            return None
        return self.parseAttemptNum(self.current_attempt.num - 1)

    def parseAttemptNum(self, num):
        num = str(num)
        if num not in self.data:
            return None
        return MazeAttempt.Make(self.data[num])

    def recordInfo(self):
        self.current_attempt.addInfo(self.robot)

# EPuck (Robot) Class
class EPuck:
    def __init__(self, robot):
        self.robot = robot
        self.laser_sensors = []
        for i in range(8):
            sensor = self.robot.getDevice(f'ps{i}')
            sensor.enable(TIME_STEP)
            self.laser_sensors.append(sensor)
        self.leftMotor = self.robot.getDevice('left wheel motor')
        self.rightMotor = self.robot.getDevice('right wheel motor')
        self.leftMotor.setPosition(float('inf'))
        self.rightMotor.setPosition(float('inf'))
        self.leftMotor.setVelocity(0.0)
        self.rightMotor.setVelocity(0.0)
        self.leftMotorSensor = self.robot.getDevice('left wheel sensor')
        self.rightMotorSensor = self.robot.getDevice('right wheel sensor')
        self.leftMotorSensor.enable(TIME_STEP)
        self.rightMotorSensor.enable(TIME_STEP)
        self.compass = self.robot.getDevice('compass')
        if self.compass:
            self.compass.enable(TIME_STEP)
        self.touchSensor = self.robot.getDevice('touch sensor')
        if self.touchSensor:
            self.touchSensor.enable(TIME_STEP)
        self.game_data = GameData(self)
        self._state = RobotState.FindWall

    def step(self):
        if self.robot.step(TIME_STEP) != -1:
            return True
        return False

    @property
    def bearing(self):
        if not self.compass:
            return None
        dir = self.compass.getValues()
        if math.isnan(dir[0]):
            return None
        rad = math.atan2(dir[0], dir[1])
        bearing = (rad - 1.5708) / math.pi * 180.0
        if bearing < 0.0:
            bearing = bearing + 360.0
        return bearing

    @property
    def direction(self):
        bearing = self.bearing
        if bearing is None:
            return None
        if 45 < bearing <= 135:
            return Direction.West
        elif 135 < bearing <= 225:
            return Direction.South
        elif 225 < bearing <= 315:
            return Direction.East
        else:
            return Direction.North

    def setSpeed(self, speed):
        speed = MAX_SPEED * (speed / 100)
        self.leftMotor.setVelocity(speed)
        self.rightMotor.setVelocity(speed)

    def setLeftWheelSpeed(self, speed):
        speed = MAX_SPEED * (speed / 100)
        self.leftMotor.setVelocity(speed)

    def setRightWheelSpeed(self, speed):
        speed = MAX_SPEED * (speed / 100)
        self.rightMotor.setVelocity(speed)

    def printSensorValues(self):
        front_left = self.laser_sensors[7].getValue()
        front_right = self.laser_sensors[0].getValue()
        side_left = self.laser_sensors[5].getValue()
        side_right = self.laser_sensors[2].getValue()

        TBL_END = "-------------------------------------------------------------------------------"
        TBL_SPACER = "|{!s:-^8}|{!s:-^8}|{!s:-^10}|{!s:-^9}|{!s:-^9}|{!s:-^10}|{!s:-^8}|{!s:-^8}|"
        TBL_HEADER = "|{!s:^8}|{!s:^8}|{!s:^10}|{!s:^9}|{!s:^9}|{!s:^10}|{!s:^8}|{!s:^8}|"
        TBL_ROW = "|{:^8.1f}|{:^8.1f}|{:^10.1f}|{:^9.1f}|{:^9.1f}|{:^10.1f}|{:^8.1f}|{:^8.1f}|"
        TABLE_STR = TBL_END + "\n" +TBL_HEADER + "\n" + TBL_SPACER + "\n" + TBL_ROW + "\n" + TBL_END + "\n"
        
        STR = TABLE_STR.format(
            "L-Back", "L-Side", "L-Corner", "L-Front", "R-Front", "R-Corner", "R-Side", "R-Back",
            '', '', '', '', '', '', '', '',
            back_left, side_left, corner_left, front_left, front_right, corner_right, side_right, back_right)
        
        print(STR)

    @property
    def state(self):
        return self._state

    @property
    def hand_rule(self):
        return self.game_data.current_attempt.rule

    @state.setter
    def state(self, state):
        self._state = state

    def run(self):
        self.travel()
        self.game_data.recordInfo()
        self.game_data.writeData()

    def travel(self):
        front_left = self.laser_sensors[7].getValue()
        front_right = self.laser_sensors[0].getValue()
        side_left = self.laser_sensors[5].getValue()
        side_right = self.laser_sensors[2].getValue()

        hand_front = None
        opposite_front = None
        hand_corner = None
        hand_side = None

        if self.hand_rule == HandRule.Right:
            hand_front = front_right
            opposite_front = front_left
            hand_corner = self.laser_sensors[1].getValue()
            hand_side = side_right
        elif self.hand_rule == HandRule.Left:
            hand_front = front_left
            opposite_front = front_right
            hand_corner = self.laser_sensors[6].getValue()
            hand_side = side_left

        touch = self.touchSensor.getValue() if self.touchSensor else 0
        if not math.isnan(touch) and touch > 0 and opposite_front < 80 and hand_front < 80:
            self.state = RobotState.GameOver
            return

        if self.state == RobotState.FindWall:
            self.setSpeed(50)
            if opposite_front > 200 and hand_front > 200:
                self.setSpeed(0)
                self.state = RobotState.MountWall
            elif opposite_front > 150 and hand_front > 150:
                self.setSpeed(5)
            elif opposite_front > 80 and hand_front > 80:
                self.setSpeed(20)
        elif self.state == RobotState.MountWall:
            if self.hand_rule == HandRule.Right:
                self.setLeftWheelSpeed(-35)
                self.setRightWheelSpeed(35)
            else:
                self.setLeftWheelSpeed(35)
                self.setRightWheelSpeed(-35)
            if opposite_front > 80:
                return
            if hand_corner < 120 and hand_side > 100:
                self.setSpeed(0)
                self.state = RobotState.FollowWall
        elif self.state == RobotState.FollowWall:
            self.setSpeed(100)
            if opposite_front > 100 and hand_front > 100:
                self.setSpeed(0)
                self.state = RobotState.MountWall
            elif hand_side < 80 and hand_corner < 80:
                self.setSpeed(50)
                self.state = RobotState.TurnCorner
            elif hand_side > 200 and hand_corner > 150:
                if self.hand_rule == HandRule.Right:
                    self.setLeftWheelSpeed(-10)
                    self.setRightWheelSpeed(50)
                else:
                    self.setLeftWheelSpeed(50)
                    self.setRightWheelSpeed(-10)
            elif hand_side > 200 and hand_corner > 100:
                if self.hand_rule == HandRule.Right:
                    self.setLeftWheelSpeed(80)
                    self.setRightWheelSpeed(100)
                else:
                    self.setLeftWheelSpeed(100)
                    self.setRightWheelSpeed(80)
            elif hand_side < 150 and hand_corner < 80:
                if self.hand_rule == HandRule.Right:
                    self.setLeftWheelSpeed(100)
                    self.setRightWheelSpeed(80)
                else:
                    self.setLeftWheelSpeed(80)
                    self.setRightWheelSpeed(100)
        elif self.state == RobotState.TurnCorner:
            if self.hand_rule == HandRule.Right:
                self.setLeftWheelSpeed(50)
                self.setRightWheelSpeed(8)
            else:
                self.setLeftWheelSpeed(8)
                self.setRightWheelSpeed(50)
            if opposite_front > 100 and hand_front > 100:
                self.setSpeed(0)
                self.state = RobotState.MountWall
            elif hand_corner > 80:
                self.setSpeed(5)
                self.state = RobotState.FollowWall

print("Starting")
robot = EPuck(Robot())
while robot.step():
    robot.run()
    if robot.state == RobotState.GameOver:
        break
print("GAME OVER")