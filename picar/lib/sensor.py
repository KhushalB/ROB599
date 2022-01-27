from utils import reset_mcu
reset_mcu()
from adc import ADC
from picarx_improved import Picarx
import numpy as np
import time


class Sensor:
    def __init__(self):
        self.chn_0 = ADC("A0")
        self.chn_1 = ADC("A1")
        self.chn_2 = ADC("A2")

    def sensor_reading(self):
        adc_value_list = []
        adc_value_list.append(self.chn_0.read())
        adc_value_list.append(self.chn_1.read())
        adc_value_list.append(self.chn_2.read())
        return adc_value_list


class Interpreter:
    def __init__(self, sensitivity=900, polarity=-1):
        self.sensitivity = sensitivity
        self.polarity = polarity  # -1 to follow darker lines, 1 to follow lighter lines

    def interpret(self, adc_values):
        # Mapping robot position between -1 and 1 based on sensor reading. Positive values correspond to the left.
        if abs(adc_values[2] - adc_values[0]) >= self.sensitivity:
            output = -((self.sensitivity + min(adc_values)) / max(adc_values)) * (self.polarity * np.sign(adc_values[2] - adc_values[0]))

            if output > 1:
                output = 1
            elif output < -1:
                output = -1

        else:
            output = 0

        return output


class Controller:
    def __init__(self, scaling=40):
        self.scaling_factor = scaling

    def control(self, output):
        px = Picarx()
        steer_angle = output * self.scaling_factor
        px.set_dir_servo_angle(steer_angle)
        time.sleep(1)

        return steer_angle


if __name__ == '__main__':
    sensor = Sensor()
    interpreter = Interpreter()
    controller = Controller()
    px = Picarx()
    px.forward(10)
    time.sleep(0.05)

    t = time.time()
    while time.time() < t+10:
        reading = sensor.sensor_reading()
        output = interpreter.interpret(reading)
        controller.control(output)
        time.sleep(0.05)
