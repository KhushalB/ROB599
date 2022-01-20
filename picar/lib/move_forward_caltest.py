import sys
sys.path.append(r'/home/pi/picar-x/lib')
from utils import reset_mcu
reset_mcu()

from picarx import Picarx
import time


if __name__ == "__main__":
    try:
        px = Picarx()
        px.set_dir_servo_angle(0)
        time.sleep(1)
        px.forward(30)
        time.sleep(2)
    finally:
        px.forward(0)
