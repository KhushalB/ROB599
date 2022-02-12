from utils import reset_mcu
reset_mcu()
from adc import ADC
from picarx_improved import Picarx
import numpy as np
import time
import concurrent.futures
from readerwriterlock import rwlock

import rosros as ros
from ultrasonic import Ultrasonic
from pin import Pin


def gray_sensor():
    while True:
        chn_0 = ADC("A0")
        chn_1 = ADC("A1")
        chn_2 = ADC("A2")
        adc_value_list = [chn_0.read(), chn_1.read(), chn_2.read()]
        return adc_value_list


def gray_interpreter(adc_values):
    sensitivity = 900
    polarity = -1

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

    return output


def ultra_sensor():
    trig_pin = Pin("D2")
    echo_pin = Pin("D3")
    sonar = Ultrasonic(trig_pin, echo_pin)
    dist = sonar.read()

    return dist


def ultra_interpreter(dist):
    return 0 < dist < 500


def controller_function(output, px):
    scaling_factor = 40

    while True:
        steer_angle = output * scaling_factor
        px.set_dir_servo_angle(steer_angle)


if __name__ == '__main__':
    px = Picarx()
    graysense_bus = ros.Bus()
    grayinterpret_bus = ros.Bus()
    ultrasense_bus = ros.Bus()
    ultrainterpret_bus = ros.Bus()
    delay = 0.1

    graysense_producer = ros.Producer(gray_sensor, graysense_bus, delay)
    grayinterpret_consumerproducer = ros.ConsumerProducer(gray_interpreter, graysense_bus, grayinterpret_bus, delay)
    ultrasense_producer = ros.Producer(ultra_sensor, ultrasense_bus, delay)
    ultrainterpret_consumerproducer = ros.ConsumerProducer(ultra_interpreter, ultrasense_bus, ultrainterpret_bus, delay)
    ros.runConcurrently([graysense_producer, grayinterpret_consumerproducer, ultrasense_producer, ultrainterpret_consumerproducer])
