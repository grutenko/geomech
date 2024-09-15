import wx
import sys
import config
import database
import sys
import traceback
import logging
import os

import options
import ui.windows.main_window.main_window
from ui.start import StartDialog
from pony.orm import *

def show_exception(e: Exception):
    message = "Uncaught exception:\n"
    message += "".join(traceback.format_exception(e.__class__, e, e.__traceback__))
    logging.exception(message)

    dlg = wx.MessageDialog(
        None, "Ошибка: " + str(e), str(e.__class__), wx.OK | wx.ICON_ERROR
    )
    dlg.ShowModal()
    dlg.Destroy()

logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(options.__PROGRAM_HOME__, "error.log"),
    filemode="a",
    format="%(asctime)s %(levelname)s %(message)s",
)

def excepthook(exception_type, exception_value, exception_traceback):
    show_exception(exception_value)


sys.excepthook = excepthook

if __name__ == "__main__":
    app = wx.App(0)

    config.configure()

    dlg = StartDialog()
    if dlg.ShowModal() != wx.ID_OK:
        sys.exit(1)

    _conf = config.get('database')
    database.init(_conf)

    main_frame = ui.windows.main_window.main_window.MainFrame(_conf)
    app.SetTopWindow(main_frame)

    app.MainLoop()
