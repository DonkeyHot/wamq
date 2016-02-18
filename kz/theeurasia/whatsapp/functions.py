'''
@author: vadim.isaev
'''
import datetime
import logging


logger = logging.getLogger(__name__)

def convertTimeStampToText(timestamp):
    if timestamp:
        time = datetime.datetime.fromtimestamp(timestamp)
        ret = time.strftime('%Y-%m-%d %H:%M:%S')
        return ret
    else:
        return None
