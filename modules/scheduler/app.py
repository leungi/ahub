import time

# local imports
from schedulermain import Scheduler

CHECK_INTERVAL = 60

apis = []
scheduler = Scheduler()

while 1:
    apis = scheduler.check_apis(apis)
    time.sleep(CHECK_INTERVAL)
