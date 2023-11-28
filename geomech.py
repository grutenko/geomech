import wx
from main_window import MainWindow
from database import init
import sys, traceback
import sqlalchemy
from database import get_session
import config
import traceback
from util import (except_hook, ask_dsn)

sys.excepthook = except_hook

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

app = wx.App(0)

if __name__ == '__main__':
    config.init_config()
    if len(config.read_config('/DatabaseUrl')) == 0:
        dsn = ask_dsn()
        if dsn == None:
            exit()
        config.write_config('/DatabaseUrl', dsn)
    init(config.read_config('/DatabaseUrl'))
    mainWindow = MainWindow(None)
    mainWindow.Show()
    app.SetTopWindow(mainWindow)
    app.MainLoop()

