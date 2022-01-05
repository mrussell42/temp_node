from requests import post
from datetime import datetime
import time
import numpy as np


def submit(value):
    #url = 'http://localhost:4040/submit'
    url = 'http://192.168.1.101:5000/submit'
    #url = 'http://192.168.1.72:4040/submit'
    now = datetime.now()
    myobj = {'dev_datestr': now.isoformat(),
             'value': value,
             'device_id': 90,
             'datatype': 'temp'}
    print("submitting", myobj)
    x = post(url, json=myobj)
    # x = requests.get("http://localhost:4040/plot/99")


def main():
    for i in range(100):
        submit(np.sin(2 * i * 0.141))
        time.sleep(1)
    
    
if __name__ == '__main__':
    main()
