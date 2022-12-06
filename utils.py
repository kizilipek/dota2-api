from datetime import datetime 
import requests 
import time
import json

class OpenDotaAPI():
    def __init__(self, verbose = False):
        self.verbose = verbose

    def _call(self, url, parameters, tries= 2):
        for i in range(tries):
            try:
                if self.verbose: print("Sending API request... ", end="", flush=True)
                resp = requests.get(url, params= parameters, timeout= 20)
                load_resp = json.loads(resp.text)
                if self.verbose: print("done")
                return load_resp
            except Exception as e:
                print("failed. Trying again in 5s")
                print(e)
                time.sleep(5)
        else:
            ValueError("Unable to connect to OpenDota API")
            
def validate(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False
        # raise ValueError("Incorrect data format, should be YYYY-MM-DD")