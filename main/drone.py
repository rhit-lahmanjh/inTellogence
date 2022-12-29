import sys
import djitellopy as tel
from enum import Enum
from perlin_noise import PerlinNoise
from feedAnalyzer import FeedAnalyzer
import cv2
import keyboard as key
import time as t
from collections import deque
import socket 

DEBUG_PRINTS = False
WITH_DRONE = True
RECORD_SENSOR_STATE = True

class State(Enum):
    Landed = 1
    Takeoff = 2
    Explore = 3
    FollowWalkway = 4
    FollowHallway = 5
    TrackPerson = 6
    Doorway = 7
    Scan = 8
    Hover = 9

class Drone(tel.Tello):
    vidCap = None
    MAXSPEED = 10
    opState = None
    prevState = None
    noise = None
    vision = None
    STOP = [0,0,0,0]
    sensorState = dict()
    
    
    def __init__(self,name):
        cv2.VideoCapture()
        super().__init__()
        self.name = name
        self.opState = State.Landed
        if WITH_DRONE:
            # This is where we will implement connecting to a drone through the router
            self.connect()
            self.set_speed(self.MAXSPEED)
            self.initializeSensorState()

            #setup video
            self.streamon()
            self.vidCap = self.get_video_capture()
            # self.VID_UDP_ADD = self.get_udp_video_address()

        #setup useful classes
        self.noise = PerlinNoise()
        self.vision = FeedAnalyzer()

    def clear_buffer(self, cap):
        """ Emptying buffer frame """
        while True:
            start_time = t.time()
            grabbed = cap.grab()
            if t.time()-start_time > .02:
                break
            
    def getFrame(self):
        self.clear_buffer(self.vidCap)
        return self.vidCap.retrieve()

    def stop(self):
        print('Stopping')
        if self.is_flying:
            self.land()
        self.vidCap.release()
        self.streamoff()
        self.end()   

    def moveDirection(self,direction = [0, 0, 0, 0]):
        """Set the speed of the drone based on xyz and yaw
        direction is:
        forward/backward : x or element 1
        side to side     : y or element 2
        up and down      : z or element 3
        yaw              : turn or element 4
        """
        cmd = f'rc {direction[1]} {direction[0]} {direction[2]} {direction[3]}'    
        self.send_command_without_return(cmd)

    def initializeSensorState(self):
        states = self.get_current_state()
        if(DEBUG_PRINTS):
            print(f'Sensor readings are{states}')
            print(f'Sensor readings are returning {type(states.get("bat"))}')
            print(f'Sensor key list is: {states.keys()}')
        for key in states:
            queue = deque()
            queue.append(states.get(key))
            self.sensorState.update({key:queue})
            
    def updateSensorState(self):
        currentStates = self.get_current_state()
        for key in currentStates:
            queue = self.sensorState.get(key)
            queue.append(currentStates.get(key))
            if(len(queue) > 10):
                queue.popleft()

    def getSensorReading(self,sensor, average = False):
        """Reads most recent appropriate sensor reading, either most recent value or most recent averaged value
            NOTE: mpry key is not supported, this function assumes integer values
        Args:
            sensor (_type_): _description_
            average (bool, optional): _description_. Defaults to False.

        Returns:
            float: _description_
        """
        if(average):
            pastXreadings = list(self.sensorState.get(sensor))
            return sum(pastXreadings)/len(pastXreadings)
        else:
            return self.sensorState.get(sensor)[-1]

    def randomWander(self,prevDirection = None):
        """Shifts a random movement vector smoothly by applying Perlin noise.

        Args:
            prevDirection (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        if prevDirection == None:
            prevDirection = [0,self.MAXSPEED/2,0,0] # this is not default argument bc using self
        print(f'Previous {prevDirection}')
        noise = self.noise(prevDirection)
        print(f'Noise{noise}')
        direction = prevDirection + noise
        print(f'Sum{direction}')
        return direction
    
    def fullScan(self):
        self.moveDirection([0,0,0,10])

    def handleUserInput(self):
        # land interrupt
        if(key.is_pressed('l')):
            self.land()
            self.opState = State.Landed
            return
        moveDist = 30
        if key.is_pressed('up'):
            self.move_up(60)
            return
        if key.is_pressed('f'):
            self.flip_back()
            return
        if key.is_pressed('down'):
            self.move_down(moveDist)
            return
        if key.is_pressed('a'):
            self.move_left(moveDist)
            return
        if key.is_pressed('d'):
            self.move_right(moveDist)
            return
        if key.is_pressed('w'):
            self.move_forward(moveDist)
            return
        if key.is_pressed('s'):
            self.move_back(moveDist)
            return
        if key.is_pressed('left'):
            self.rotate_counter_clockwise(45)
            return
        if key.is_pressed('right'):
            self.rotate_clockwise(45)
            return

    def dronelessTest(self):
        while cv2.waitKey(20) != 27: # Escape
            self.randomWander()
    
    def testFunction(self):
        while cv2.waitKey(20) != 27: # Escape
            print(self.get_battery())

    def operate(self):
        # creating window
        if(WITH_DRONE):
            cv2.namedWindow('test', cv2.WINDOW_NORMAL)

        #Static Telemetry Checks before Takeoff

        # Checks the battery charge before takeoff
        if self.getSensorReading("bat") > 50:
            BatCheck = True
        else:
            BatCheck = False
            BatReason = "Battery Charge Too Low"

        # Checks the highest battery temperature before takeoff
        if self.getSensorReading("temph") < 100:
            TemphCheck = True
        else:
            TemphCheck = False
            TemphReason = "Battery Temperature Too High"

        # Checks the baseline low temperature before takeoff
        if self.getSensorReading("templ") < 90:
            TemplCheck = True
        else:
            TemplCheck = False
            TemplReason = "Baseline Low Temperature Too High"

        # Turns the string SNR value into an integer
        # Checks the Wi-Fi SNR value to determine signal strength
        signalStrength = self.query_wifi_signal_noise_ratio()
        signalStrengthInt = int(signalStrength)
        if signalStrengthInt > 15:
            SignalCheck = True
        else:
            SignalCheck = False
            SignalReason = "SNR below 15dB. Weak Connection"

        # Checks to make sure the pitch is not too far off
        # If the drone is too far from 0 degrees on pitch the takeoff
        # could be unsafe
        pitch = self.getSensorReading("pitch")
        if pitch < 10 or pitch > -10:
            pitchCheck = True
        else:
            pitchCheck = False
            pitchReason = "Pitch is Off Center. Unstable Takeoff."

        # Checks to make sure the roll is not too far off
        # If the drone is too far from 0 degrees on roll the takeoff
        # could be unsafe
        roll = self.getSensorReading("roll")
        if roll < 10 or roll > -10:
            rollCheck = True
        else:
            rollCheck = False
            rollReason = "Roll is Off Center. Unstable Takeoff."

        # Comment out function as needed until testing can confirm desired threshold value
        # Checks to ensure the drone is at a low enough height to ensure room during takeoff for safe ascent
        if self.getSensorReading("h") < 1000:
            HeightCheck = True
        else:
            HeightCheck = False
            HeightReason = ("Drone is Too High")

        # Dictionary of Boolean values to check through static telemetry
        telemetryCheck = {"bat":[BatCheck], "temph":[TemphCheck], "templ":[TemplCheck],
                          "SignalStrength":[SignalCheck], "pitch":[pitchCheck], "roll":[rollCheck],
                          "height":[HeightCheck]}

        telemetryReason = {"bat":[BatReason], "temph":[TemphReason], "templ":[TemplReason],
                          "SignalStrength":[SignalReason], "pitch":[pitchReason], "roll":[rollReason],
                          "height":[HeightReason]}
        res = True
        for key, value in telemetryCheck.items():
            print(key, value)
            # Test Boolean Value of Dictionary
            # Using all() + values()
            # Do key value pairs need to be flipped to use the all method
            res = all(telemetryCheck.values())
            if not res:
                self.land()
                self.stop()
                self.end()
                print("A Telemetry threshold has been violated. Please review dictionary output. ")
            else:
                self.takeoff()

        # general loop
        while cv2.waitKey(20) != 27: # Escape
            if DEBUG_PRINTS:
                print("looping")

            # Dynamic Telemetry Checks to monitor while in flight, is it possible to reuse the dictionary?
            # Dynamic Battery Temp, Dynamic Battery Charge, Dynamic Wi-Fi SNR, Dynamic Pitch and Roll Controls
            res = True
            for key, value in telemetryCheck.items():
                print(key, value)
                # Test Boolean Value of Dictionary
                # Using all() + values()
                # Do key value pairs need to be flipped to use the all method
                res = all(telemetryCheck.values())
                if not res:
                    self.land()
                    print("A Telemetry threshold has been violated. Please review dictionary output. ")

            # Dynamic Safety functions to respond to visual input

            # get and analyze visual stimulus
            returned, img = self.getFrame()
            if returned:
                print('Seeing')
                objects = self.vision.detect_objects(img)
                self.vision.display_objects(img, objects,threshold=.9)
                cv2.imshow('test', img)

                # initial demo IO, soon to be removed
                for object in objects[0,0,:,:]:
                    if object[2] < .8:
                        break
                    if object[1] == 77:
                        cellPhoneCounter = cellPhoneCounter + 1
                    if object[1] == 77 and cellPhoneCounter == 2:
                        # self.prevState = self.opState
                        # self.opState = State.Hover
                        # self.flip_back()
                        print(f'Cell Phone detected. Flipping')
                        cellPhoneCounter = 0
                        break

            self.handleUserInput()

            #State Switching SIILL IN DEV
            match self.opState:
                case State.Landed:
                    if key.is_pressed('t'):
                        self.opState = State.Takeoff
                    print('Landed')
                case State.Takeoff:
                    self.takeoff()
                    self.opState = State.Scan
                    print('Takeoff')
                case State.Scan:
                    # self.fullScan()
                    print('do nothing')
                case State.Explore:
                    self.moveDirection(self.randomWander())
                case State.Hover():
                    self.moveDirection(self.STOP)
        self.stop()
        cv2.destroyAllWindows()


drone1 = Drone('chuck')
# drone1.dronelessTest()

drone1.initializeSensorState()
print(drone1.sensorState.keys())
for i in range(0,12):
    drone1.updateSensorState()
print(drone1.getSensorReading('tof',average=True))
print('stop')
# drone1.testFunction()