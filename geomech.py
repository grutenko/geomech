# _*_ coding: UTF8 _*_

import wx
import sys, traceback
import database
from sqlalchemy.exc import SQLAlchemyError
import config
import traceback
import list_windows
import util
import logging
from sys import exit

logging.basicConfig(
    level=logging.INFO,
    filename="geomech.log",
    filemode="a",
    format="%(asctime)s %(levelname)s %(message)s")

sys.excepthook = util.except_hook

app = wx.App(0)

def read_dsn() -> str:
    return "postgresql://{0}:{1}@{2}:{3}/{4}".format(
            config.read_option('database', 'user'), 
            config.read_option('database', 'password'), 
            config.read_option('database', 'ip'), 
            config.read_option('database', 'port'), 
            config.read_option('database', 'name'))

def main():
    config.init_config()

    logging.info("--- STARTED ---")

    if config.has_option('database', 'user') \
            and config.has_option('database', 'password') \
            and config.has_option('database', 'ip') \
            and config.has_option('database', 'port') \
            and config.has_option('database', 'name'):
        try:
            database.test_connection(read_dsn())
        except (SQLAlchemyError, database.xDatabaseInitError) as e:
            conn_success = False
            util.except_hook(type(e), e, e.__traceback__)
        else:
            conn_success = True
    else:
        conn_success = False

    if not conn_success:
        if not util.ask_dsn():
            exit()

    database.init_database(read_dsn())

    mainWindow = list_windows.cmd_show(database.DischargeMeasurement)
    app.SetTopWindow(mainWindow)
    app.MainLoop()

if __name__ == '__main__':
    main()