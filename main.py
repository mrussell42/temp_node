from time import sleep, time
from machine import ADC, unique_id, Pin, RTC, I2C
from urequests import post
import ntptime
from ustruct import unpack
from micropython import const

DEBUG = False
READ_INVERVAL = 60*10
NREADS = 100.

AHTX0_I2CADDR_DEFAULT = const(0x38)  # Default I2C address
AHTX0_CMD_CALIBRATE = const(0xE1)  # Calibration command
AHTX0_CMD_TRIGGER = const(0xAC)  # Trigger reading command
AHTX0_CMD_SOFTRESET = const(0xBA)  # Soft reset command
AHTX0_STATUS_BUSY = const(0x80)  # Status bit for busy
AHTX0_STATUS_CALIBRATED = const(0x08)  # Status bit for calibrated


class AM2301():
    def __init__(self, SDApin=4, SCLpin=5):
        sleep(0.1)
        self._buf = bytearray(6)
        self._temp = None
        self._humidity = None
        self.i2c = I2C(scl=Pin(SCLpin), sda=Pin(SDApin), freq=100000)
        self.reset()
    
    def reset(self):
        self._buf[0] = 0x71
        self.write(self._buf, start=0, end=1)
        sleep(0.02)

    def calibrate(self):
        """Ask the sensor to self-calibrate. Returns True on success, False otherwise"""
        self._buf[0] = AHTX0_CMD_CALIBRATE
        self._buf[1] = 0x08
        self._buf[2] = 0x00
        self.write(self._buf, start=0, end=3)
        while self.status & AHTX0_STATUS_BUSY:
            sleep(0.01)
        if not self.status & AHTX0_STATUS_CALIBRATED:
            return False
        return True

    @property
    def status(self):
        """The status byte initially returned from the sensor, see datasheet for details"""
        ret_data = unpack('>B',self.i2c.readfrom(AHTX0_I2CADDR_DEFAULT, 1))[0]
        # print("status: " + str(ret_data))
        return ret_data
    
    @property
    def relative_humidity(self):
        """The measured relative humidity in percent."""
        self._readdata()
        return self._humidity

    @property
    def temperature(self):
        """The measured temperature in degrees Celsius."""
        self._readdata()
        return self._temp
    
    def _readdata(self):
        """Internal function for triggering the AHT to read temp/humidity"""
        self._buf[0] = AHTX0_CMD_TRIGGER
        self._buf[1] = 0x33
        self._buf[2] = 0x00
        self.write(self._buf, start=0, end=3)
        
        while self.status & AHTX0_STATUS_BUSY:
            sleep(0.01)
        self.i2c.readfrom_into(AHTX0_I2CADDR_DEFAULT, self._buf)
    
        self._humidity = (
            (self._buf[1] << 12) | (self._buf[2] << 4) | (self._buf[3] >> 4)
        )
        self._humidity = (self._humidity * 100) / 0x100000
        self._temp = ((self._buf[3] & 0xF) << 16) | (self._buf[4] << 8) | self._buf[5]
        self._temp = ((self._temp * 200.0) / 0x100000) - 50
        
    def write(self, b, start=0, end=None):
        if end is None:
            end = len(b)
        self.i2c.writeto(AHTX0_I2CADDR_DEFAULT, b[start:end])
    



class TSensor():
    """Sensor class which can read the adc and return a temperaure"""
    def __init__(self):
        self.adc = ADC(0)

    def read_temp(self):
        adc = self.adc
        adc.read()
        adc_sum = 0

        for _i in range(int(NREADS)):
            sleep(0.01)
            # TMP36 is 100 degC / V
            voltage = self.read_voltage() 
           
            adc_sum += (voltage - 0.5) * 100.
	#print(adc_sum/100.)
        return adc_sum / NREADS
	
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
    ts = AM2301()
    ts.calibrate()
    
    #ts = TSensor()
    #p0 = Pin(0, Pin.OUT)
    #p16 = Pin(16, Pin.OUT)
    t0 = time() - READ_INVERVAL
    t_updatetime = time()
    
    #p0.on()
    #p16.on()
    
    
    while True:
        if (time() - t0) > READ_INVERVAL:
            t0 = time()
            temperature_sum = 0
            for i in range(int(NREADS)):
                try: 
                    temperature_sum += ts.temperature
                except:
                    pass
                sleep(0.05)
            temperature = temperature_sum / NREADS
                

            #p0.on()
            #p16.on()
            # temperature = ts.read_temp()
            #p0.off()
            #p16.off()
            yy, mo, dd, wd, hh, mm, ss, msec = rtc.datetime()
            datestr = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}.{:06d}".format(yy, mo, dd, hh, mm, ss, msec)
            
            myobj = {'dev_datestr': datestr,
                     'id': unpack('>I',unique_id())[0],
                     'value': temperature,
                     'device_id': 92,
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
