# -*- coding: utf-8 -*-
'''
@author: vadim.isaev
'''
import datetime
import json
import logging
import signal


logger = logging.getLogger(__name__)

SIGNALS_TO_NAMES_DICT = dict((getattr(signal, n), n) \
    for n in dir(signal) if n.startswith('SIG') and '_' not in n )

def convertTimeStampToText(timestamp):
    if timestamp:
        time = datetime.datetime.fromtimestamp(timestamp)
        ret = time.strftime('%Y-%m-%d %H:%M:%S')
        return ret
    else:
        return None

def safeJsonDecode(jsonString):
    return json.loads(jsonString, object_hook=_byteify)

def safeJsonEncode(jsonStruct):
    return json.dumps(jsonStruct, indent=3)

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data
