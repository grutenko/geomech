# _*_ coding: UTF8 _*_

import wx
import sys, traceback
from database import Credentials, configure as configure_database, session as database_session, DischargeMeasurement
from sqlalchemy.exc import SQLAlchemyError
import config
import traceback
import list_windows
import util
import logging
import typing
import dialogs
from sys import exit

logging.basicConfig(
    level=logging.INFO,
    filename="geomech.log",
    filemode="a",
    format="%(asctime)s %(levelname)s %(message)s")

def except_hook(exception_type, exception_value, exception_traceback):
    util.show_exception(exception_value)

sys.excepthook = except_hook

class App(wx.App):
    def OnInit(self):
        logging.info("--- STARTED ---")
        config.configure("geomech.ini")
        if not config.has_section("database"):
            credentials = util.ask_credentials()
            if credentials == None:
                exit()
            config.write_database_credentials(credentials)
        else:
            credentials = config.read_database_credentials()
        configure_database(credentials)
        mainWindow = list_windows.cmd_show(DischargeMeasurement)
        self.SetTopWindow(mainWindow)

        return True

def main():
    app = App(0, useBestVisual=True)
    app.MainLoop()

if __name__ == '__main__':
    main()