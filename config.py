# _*_ coding: UTF8 _*_

import io
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser
import os
from attrdict2 import AttrDict
from database import Credentials

config: AttrDict = None

def configure(path: str):
    global config
    _config = ConfigParser()
    if not os.path.exists(path):
        with open(path, 'a'):
            os.utime(path, None)
    _config.read(path)
    config = AttrDict({
        "config": _config,
        "path": path
    })

def has_section(section: str) -> bool:
    global config
    if config == None:
        raise Exception("Config not initialized. Use configure() for it.")
    return config["config"].has_section(section)

def has_option(section: str, key: str):
    global config
    if config == None:
        raise Exception("Config not initialized. Use configure() for it.")
    return config["config"].has_section(section) and config["config"].has_option(section, key)
    
def read_option(section: str, key: str):
    global config
    if config == None:
        raise Exception("Config not initialized. Use configure() for it.")
    if not config["config"].has_section(section):
        return None
    return config["config"].get(section, key)
    
def write_option(section: str, key: str, value: str):
    global config
    if config == None:
        raise Exception("Config not initialized. Use configure() for it.")
    if not config["config"].has_section(section):
        config["config"].add_section(section)
    config["config"].set(section, key, str(value))
    with open(config.path, 'w') as file:
        config["config"].write(file)

def read_database_credentials() -> Credentials:
    global config
    if not has_section("database"):
        return None
    credentials = Credentials(
        user=read_option("database", "user"),
        password=read_option("database", "password"),
        host=read_option("database", "host"),
        database=read_option("database", "database"),
        port=read_option("database", "port"))
    return credentials

def write_database_credentials(credentials: Credentials):
    write_option('database', 'user', credentials.user), 
    write_option('database', 'password', credentials.password), 
    write_option('database', 'host', credentials.host), 
    write_option('database', 'port', credentials.port), 
    write_option('database', 'database', credentials.database)