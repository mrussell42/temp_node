from machine import ADC, unique_id
from time import sleep
import urequests
import ujson

class TSensor(object):
    def __init__(self):
        self.adc = ADC(0)

    def read_temp(self):
        adc = self.adc
        adc.read()
        sum = 0
        for i in range(100):
            sleep(0.01)
            sum = sum + ((3.3 * adc.read_u16()/ 65535.) - 0.5) * 100 # TMP36 is 100 degC / V

        return sum / 100.

def main():
    ts = TSensor()
    for i in range(10):
        temperature = ts.read_temp()
        json = ujson.dumps({'id':unique_id(), 'temperature': temperature})
        print(json)
        try:
            urequests.request(urequests.put,
                              "http://192.168.1.101/temperature_submit/",
                              json=json)
        except OSError as e:
            print("Failed to submit data", e)
            pass
        sleep(1)

if __name__ == '__main__':
    main()
