# _*_ coding: UTF8 _*_

import io
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser
import os


__CONFIGPATH__ = 'geomech.ini'
__config = ConfigParser()

def init_config():
    global __config
    if not os.path.exists(__CONFIGPATH__):
        with open(__CONFIGPATH__, 'a'):
            os.utime(__CONFIGPATH__, None)
    __config.read(__CONFIGPATH__)

def has_option(section: str, key: str):
    global __config
    return __config.has_section(section) and __config.has_option(section, key)
    
def read_option(section: str, key: str):
    global __config
    if not __config.has_section(section):
        return None
    return __config.get(section, key)
    
def write_option(section: str, key: str, value: str):
    global __config
    if not __config.has_section(section):
        __config.add_section(section)
    __config.set(section, key, str(value))
    with open(__CONFIGPATH__, 'w') as file:
        __config.write(file)