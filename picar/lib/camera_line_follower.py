import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import math
import numpy as np


class LineFollower:
    def __init__(self, car=None):
        self.car = car
        self.curr_steer_angle = 90

    def follow_lane(self, frame):
        lanes, frame = self.detect_lane(frame)
        final_frame = self.steer(frame, lanes)

        return final_frame

    def steer(self, frame, lanes):
        lanes_length = len(lanes)
        if lanes_length == 0:
            return frame

        new_steer_angle = self.get_steer_dir(frame, lanes):
        # self.curr_steer_angle = stabilize_steer(self.curr_steer_angle, new_steer_angle, lanes_length)

        curr_frame = display_frame(frame, self.curr_steer_angle)
        show_image('heading', curr_frame)

        return  curr_frame

    def detect_lane(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        show_image("hsv", hsv)
        lower_blue = np.array([30, 40, 0])
        upper_blue = np.array([150, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        show_image("blue mask", mask)

        # detect edges
        edges = cv2.Canny(mask, 200, 400)
        show_image('edges', edges)

        return edges

    def get_steer_dir(self, frame, lanes):
        if len(lanes) == 0:
            return -90

        height, width, _ = frame.shape
        if len(lanes) == 1:
            x1, _, x2, _ = lanes[0][0]
            x_offset = x2 - x1
        else:
            _, _, left_x2, _ = lanes[0][0]
            _, _, right_x2, _ = lanes[1][0]
            camera_mid_offset_percent = 0.02  # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
            mid = int(width / 2 * (1 + camera_mid_offset_percent))
            x_offset = (left_x2 + right_x2) / 2 - mid

        # find the steering angle, which is angle between navigation direction to end of center line
        y_offset = int(height / 2)

        angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
        angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
        steering_angle = angle_to_mid_deg  # this is the steering angle needed by picar front wheel

        return steering_angle


if __name__ == '__main__':
    # init camera
    print("start color detect")
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 24
    rawCapture = PiRGBArray(camera, size=camera.resolution)

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):  # use_video_port=True
        controller = LineFollower()
        controller.follow_lane(frame)
        controller.steer(frame, controller.detect_lane(frame))
