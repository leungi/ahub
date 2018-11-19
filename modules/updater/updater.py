import time
import config

# local imports
from checkapis import Checker

DEBUG = False

# ----------------------------------------------------------
# BOSS
# ----------------------------------------------------------
if DEBUG:
    config.NGINXHOST = config.DEBUGHOST

apis = []
checker = Checker()

while 1:
    apis = checker.check_apis(apis)
    time.sleep(config.CHECK_INTERVAL)
