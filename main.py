from time import sleep, time
from machine import ADC, unique_id, Pin, RTC
from urequests import post
import ntptime
from ustruct import unpack

DEBUG = False
READ_INVERVAL = 60*10

class TSensor():
    """Sensor class which can read the adc and return a temperaure"""
    def __init__(self):
        self.adc = ADC(0)

    def read_temp(self):
        adc = self.adc
        adc.read()
        adc_sum = 0
        nreads = 1000.
        for _i in range(int(nreads)):
            sleep(0.01)
            # TMP36 is 100 degC / V
            voltage = self.read_voltage() 
           
            adc_sum += (voltage - 0.5) * 100.
	#print(adc_sum/100.)
        return adc_sum / nreads
	
    def read_voltage(self):
    	adc = self.adc
    	adcval = adc.read_u16()
    	voltage = adcval * 3.2 / 65535
    	if DEBUG:
    	    print("Voltage: ", voltage)
    	return voltage
    	
    def __repr__(self):
        return "TMP36 ADC"


def main():
    url = 'http://192.168.1.101:5000/submit'
    rtc = RTC()
    ts = TSensor()
    p0 = Pin(0, Pin.OUT)
    p16 = Pin(16, Pin.OUT)
    timer = 0
    t0 = time()
    t_updatetime = time()
    
    p0.on()
    p16.on()
    
    while True:
        if (time() - t0) > READ_INVERVAL:
            t0 = time()
            p0.on()
            p16.on()
            temperature = ts.read_temp()
            p0.off()
            p16.off()
            yy, mo, dd, wd, hh, mm, ss, msec = rtc.datetime()
            datestr = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}.{:06d}".format(yy, mo, dd, hh, mm, ss, msec)
            
            myobj = {'dev_datestr': datestr,
                     'id': unpack('>I',unique_id())[0],
                     'value': temperature,
                     'device_id': 91,
                     'datatype': 'temp'}
            print(myobj)
        
        
            try:
                resp = post(url, json=myobj)
                resp.close()
            
            except OSError as e:
                print("Failed to submit data", url, e)
        else:
            sleep(5)
            
        if (time() - t_updatetime) > (4*3600):
            print("Updating time")
            if net.isconnected():
                try:
                    ntptime.settime()
                except:
                    print("Failed to set time")
                        
            t_updatetime = time()



if __name__ == '__main__':
    main()
