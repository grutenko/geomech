import wx

__config: wx.FileConfig = None

__CONFIG_APP_NAME__ = 'geomech'
__CONFIG_APP_VENDOR__ = 'mountine_institute'

def init_config():
    global __config
    if not __config is None:
        raise Exception("Config already initialized.")
    __config = wx.FileConfig(__CONFIG_APP_NAME__, __CONFIG_APP_VENDOR__, style=wx.CONFIG_USE_LOCAL_FILE)

def read_config(key: str, defaultVal = wx.EmptyString):
    global __config
    return __config.Read(key, defaultVal)
    
def write_config(key: str, value: str):
    global __config
    if not __config.Write(key, value):
        raise Exception("Error writing to config.")