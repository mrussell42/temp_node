import gc
import uos
import machine
import utime as time
import wificonf
import esp
import network
#import volume


# Duplicate the REPL so we can see import usocketit over the USB connection
uos.dupterm(machine.UART(0, 115200), 1)




def connect_wifi():
    """
    Connect to the wifi
    """
    net = network.WLAN(network.STA_IF)
    ssid = wificonf.WIFI_SSID
    password = wificonf.WIFI_PASSWORD
    config = wificonf.WIFI_CONFIG
    if not net.isconnected():


        print('Connecting to network {:s}...'.format(ssid))
        net.active(True)
        net.ifconfig(config)
        net.connect(ssid, password)
        t = time.ticks_ms()
        while time.ticks_ms() < (t + 30000) and not net.isconnected():
            # Wait for connection
            pass
            #print("Waiting for connection")
    if net.isconnected():
        print("Connected to", ssid)

    #print('Network config:', net.ifconfig())


gc.collect()
esp.osdebug(None) # turn off vendor O/S debugging messages
connect_wifi()
