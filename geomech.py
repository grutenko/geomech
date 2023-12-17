# _*_ coding: UTF8 _*_

import wx
import sys, traceback
import database
from sqlalchemy.exc import SQLAlchemyError
import config
import traceback
import list_windows
import dialogs
import util

sys.excepthook = util.except_hook

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = wx.App(0)

def read_dsn() -> str:
    return "postgresql://{0}:{1}@{2}:{3}/{4}".format(
            config.read_option('database', 'user'), 
            config.read_option('database', 'password'), 
            config.read_option('database', 'ip'), 
            config.read_option('database', 'port'), 
            config.read_option('database', 'name'))

if __name__ == '__main__':
    config.init_config()

    if not config.has_option('database', 'user') \
            or not config.has_option('database', 'password') \
            or not config.has_option('database', 'ip') \
            or not config.has_option('database', 'port') \
            or not config.has_option('database', 'name'):
        conn_success = False
    else:
        try:
            database.test_connection(read_dsn())
        except (SQLAlchemyError, database.xDatabaseInitError) as e:
            conn_success = False
            util.except_hook(type(e), e, e.__traceback__)
        else:
            conn_success = True

    if not conn_success:
        util.ask_dsn()
    try:
        database.init_database(read_dsn())
    except (SQLAlchemyError, database.xDatabaseInitError) as e:
        raise e

    mainWindow = list_windows.cmd_show(database.DischargeMeasurement)
    app.SetTopWindow(mainWindow)
    app.MainLoop()

