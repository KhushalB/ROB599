import sys
sys.path.append(r'/home/pi/ROB599/picar/lib')
from utils import reset_mcu
reset_mcu()

from picarx_improved import Picarx
import time


if __name__ == "__main__":
        px = Picarx()
        px.set_dir_servo_angle(0)
        time.sleep(1)
        px.forward(30)
        time.sleep(1)
        px.forward(0)
