#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/khushal/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *
from perception import Perception

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)


class Move:
    def __init__(self):
        self.servo1 = 500
        self.count = 0
        self.track = False
        self._stop = False
        self.get_roi = False
        self.center_list = []
        self.first_move = True
        self.__isRunning = False
        self.detect_color = 'None'
        self.action_finish = True
        self.start_pick_up = False
        self.start_count_t1 = True
        self.rect = None
        self.size = (640, 480)
        self.rotation_angle = 0
        self.unreachable = False
        self.world_X, world_Y = 0, 0
        self.world_x, world_y = 0, 0
        # Positioning coordinates of different color wooden buttons(x, y, z)
        self.coordinate = {
            'red': (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5, 1.5),
            'blue': (-15 + 0.5, 0 - 0.5, 1.5),
        }

    def initMove(self):
        Board.setBusServoPulse(1, self.servo1 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

    def setBuzzer(self, timer):
        Board.setBuzzer(0)
        Board.setBuzzer(1)
        time.sleep(timer)
        Board.setBuzzer(0)

    # Set the color of the RGB lights of the expansion board to match the color to be tracked
    def set_rgb(self, color):
        if color == "red":
            Board.RGB.setPixelColor(0, Board.PixelColor(255, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(255, 0, 0))
            Board.RGB.show()
        elif color == "green":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 255, 0))
            Board.RGB.show()
        elif color == "blue":
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 255))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 255))
            Board.RGB.show()
        else:
            Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
            Board.RGB.setPixelColor(1, Board.PixelColor(0, 0, 0))
            Board.RGB.show()

    def reset(self):
        self.count = 0
        self.track = False
        self._stop = False
        self.get_roi = False
        self.center_list = []
        self.first_move = True
        self.__isRunning = False
        self.detect_color = 'None'
        self.action_finish = True
        self.start_pick_up = False
        self.start_count_t1 = True

    # app initialization call
    def init(self):
        print("ColorTracking Init")
        self.initMove()

    # The app starts to play the game call
    def start(self):
        self.reset()
        self.__isRunning = True
        print("ColorTracking Start")

    # app stops gameplay calls
    def stop(self):
        self._stop = True
        self.__isRunning = False
        print("ColorTracking Stop")

    # The app exits the gameplay call
    def exit(self):
        self._stop = True
        self.__isRunning = False
        print("ColorTracking Exit")

    def move(self):
        while True:
            if self.__isRunning:
                if self.first_move and self.start_pick_up:  # When an object is first detected
                    self.action_finish = False
                    self.set_rgb(detect_color)
                    self.setBuzzer(0.1)
                    result = AK.setPitchRangeMoving((self.world_X, self.world_Y - 2, 5), -90, -90,
                                                    0)  # Do not fill in the running time parameter, adaptive running time
                    if result == False:
                        self.unreachable = True
                    else:
                        self.unreachable = False
                    time.sleep(result[2] / 1000)  # The third item of the returned parameter is the time
                    self.start_pick_up = False
                    self.first_move = False
                    self.action_finish = True
                elif not self.first_move and not self.unreachable:  # Not the first time an object has been detected
                    self.set_rgb(detect_color)
                    if self.track:  # If it is the tracking phase
                        if not self.__isRunning:  # stop and exit flag detection
                            continue
                        AK.setPitchRangeMoving((self.world_x, self.world_y - 2, 5), -90, -90, 0, 20)
                        time.sleep(0.02)
                        self.track = False
                    if self.start_pick_up:  # If the object has not moved for a while, start gripping
                        self.action_finish = False
                        if not self.__isRunning:  # stop and exit flag detection
                            continue
                        Board.setBusServoPulse(1, self.servo1 - 280, 500)  # paws open
                        # Calculate the angle by which the gripper needs to be rotated
                        servo2_angle = getAngle(self.world_X, self.world_Y, self.rotation_angle)
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.8)

                        if not self.__isRunning:
                            continue
                        AK.setPitchRangeMoving((self.world_X, self.world_Y, 2), -90, -90, 0, 1000)  # lower the altitude
                        time.sleep(2)

                        if not self.__isRunning:
                            continue
                        Board.setBusServoPulse(1, self.servo1, 500)  # Gripper closed
                        time.sleep(1)

                        if not self.__isRunning:
                            continue
                        Board.setBusServoPulse(2, 500, 500)
                        AK.setPitchRangeMoving((self.world_X, self.world_Y, 12), -90, -90, 0, 1000)  # The robotic arm is raised
                        time.sleep(1)

                        if not self.__isRunning:
                            continue
                        # Sort and place blocks of different colors
                        result = AK.setPitchRangeMoving((self.coordinate[detect_color][0], self.coordinate[detect_color][1], 12),
                                                        -90, -90, 0)
                        time.sleep(result[2] / 1000)

                        if not self.__isRunning:
                            continue
                        servo2_angle = getAngle(self.coordinate[detect_color][0], self.coordinate[detect_color][1], -90)
                        Board.setBusServoPulse(2, servo2_angle, 500)
                        time.sleep(0.5)

                        if not self.__isRunning:
                            continue
                        AK.setPitchRangeMoving(
                            (self.coordinate[detect_color][0], self.coordinate[detect_color][1], self.coordinate[detect_color][2] + 3),
                            -90, -90, 0, 500)
                        time.sleep(0.5)

                        if not self.__isRunning:
                            continue
                        AK.setPitchRangeMoving((self.coordinate[detect_color]), -90, -90, 0, 1000)
                        time.sleep(0.8)

                        if not self.__isRunning:
                            continue
                        Board.setBusServoPulse(1, self.servo1 - 200, 500)  # Claws open to drop objects
                        time.sleep(0.8)

                        if not self.__isRunning:
                            continue
                        AK.setPitchRangeMoving((self.coordinate[detect_color][0], self.coordinate[detect_color][1], 12), -90, -90,
                                               0, 800)
                        time.sleep(0.8)

                        self.initMove()  # return to original position
                        time.sleep(1.5)

                        self.detect_color = 'None'
                        self.first_move = True
                        self.get_roi = False
                        self.action_finish = True
                        self.start_pick_up = False
                        self.set_rgb(detect_color)
                    else:
                        time.sleep(0.01)
            else:
                if self._stop:
                    self._stop = False
                    Board.setBusServoPulse(1, self.servo1 - 70, 300)
                    time.sleep(0.5)
                    Board.setBusServoPulse(2, 500, 500)
                    AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
                    time.sleep(1.5)
                time.sleep(0.01)


if __name__ == '__main__':
    AK = ArmIK()
    color_tracker = Perception()
    controller = Move()
    controller.init()
    controller.start()
    controller.__target_color = ('red',)
    my_camera = Camera.Camera()
    my_camera.camera_open()
    while True:
        img = my_camera.frame
        if img is not None:
            frame = img.copy()
            Frame = color_tracker.run(frame)
            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
    my_camera.camera_close()
    cv2.destroyAllWindows()