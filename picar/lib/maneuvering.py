import sys
sys.path.append(r'/home/pi/ROB599/picar/lib')
from utils import reset_mcu

reset_mcu()

from picarx_improved import Picarx
import time

px = Picarx()


def forward_backward(steer_angle=0):
    px.set_dir_servo_angle(steer_angle)
    time.sleep(1)
    px.forward(30)
    time.sleep(2)
    px.stop()
    px.backward(30)
    time.sleep(2)
    px.stop()


def parallel_parking():
    # turn wheels and back up
    px.set_dir_servo_angle(30)
    time.sleep(0.5)
    px.backward(15)
    time.sleep(2)

    # turn wheels in opposite direction while backing up
    for angle in range(30, -30, -1):
        px.set_dir_servo_angle(angle)
        time.sleep(0.01)

    # zero out wheels
    for angle in range(-30, 0, 1):
        px.set_dir_servo_angle(angle)
        time.sleep(0.01)

    # move forward a little and stop
    px.forward(15)
    time.sleep(0.5)
    px.stop()


def three_point_turn():
    px.forward(15)
    time.sleep(2)
    for angle in range(0, -30, -1):
        px.set_dir_servo_angle(angle)
        time.sleep(0.01)

    px.stop()
    px.set_dir_servo_angle(30)
    px.backward(15)
    time.sleep(2)

    for angle in range(30, 0, -1):
        px.set_dir_servo_angle(angle)
        time.sleep(0.01)

    px.stop()


if __name__ == "__main__":
    while True:
        print("Select a maneuver:\n"
              "a: forward-backward\n"
              "b: parallel parking\n"
              "c: three-point turn\n"
              "q: quit")

        maneuver = input()

        if maneuver == "a":
            forward_backward()
        elif maneuver == "b":
            parallel_parking()
        elif maneuver == "c":
            three_point_turn()
        elif maneuver == "q":
            break
