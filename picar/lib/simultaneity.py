from utils import reset_mcu
reset_mcu()
from adc import ADC
from picarx_improved import Picarx
import numpy as np
import time
import concurrent.futures
from readerwriterlock import rwlock


class Bus:
    def __init__(self):
        self.message = []
        self.lock = rwlock.RWLockWriteD()

    def read(self):
        with self.lock.gen_rlock():
            message = self.message

        return message

    def write(self, message):
        with self.lock.gen_wlock():
            self.message = message


class SensorBus(Bus):
    pass


class InterpreterBus(Bus):
    pass


def sensor_function(sensor_bus, delay):
    while True:
        chn_0 = ADC("A0")
        chn_1 = ADC("A1")
        chn_2 = ADC("A2")
        adc_value_list = [chn_0.read(), chn_1.read(), chn_2.read()]
        sensor_bus.write(message=adc_value_list)
        time.sleep(delay)


def interpreter_function(sensor_bus, interpreter_bus, delay):
    sensitivity = 900
    polarity = -1

    while True:
        adc_values = sensor_bus.read()

        # Mapping robot position between -1 and 1 based on sensor reading. Positive values correspond to the left.
        if abs(adc_values[2] - adc_values[0]) >= sensitivity:
            output = -((sensitivity + min(adc_values)) / max(adc_values)) * (
                        polarity * np.sign(adc_values[2] - adc_values[0]))

            if output > 1:
                output = 1
            elif output < -1:
                output = -1

        else:
            output = 0

        interpreter_bus.write(message=output)
        time.sleep(delay)


def controller_function(interpreter_bus, delay, px):
    scaling_factor = 40

    while True:
        output = interpreter_bus.read()
        steer_angle = output * scaling_factor
        px.set_dir_servo_angle(steer_angle)
        time.sleep(delay)


if __name__ == '__main__':
    px = Picarx()
    px.forward(10)
    time.sleep(0.05)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        sensor_bus = SensorBus()
        interpreter_bus = InterpreterBus()
        delay = 0.1

        eSensor = executor.submit(sensor_function, sensor_bus, delay)
        eInterpreter = executor.submit(interpreter_function, sensor_bus, interpreter_bus, delay)
        eController = executor.submit(controller_function, interpreter_bus, delay, px)

    eSensor.result()
