import logging
import os
import sys
import traceback

import wx

import config
import database
import options
import ui.windows.main.main
import ui.icon
from ui.start import StartDialog


class MyApp(wx.App):

    def OnInit(self):
        return True


if __name__ == "__main__":

    def show_exception(e: Exception):
        message = "Uncaught exception:\n"
        message += "".join(traceback.format_exception(e.__class__, e, e.__traceback__))
        logging.exception(message)

        dlg = wx.MessageDialog(None, "Ошибка: " + str(e), str(e.__class__), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def excepthook(exception_type, exception_value, exception_traceback):
        show_exception(exception_value)

    sys.excepthook = excepthook

    if os.name != "nt":
        ui.icon.icon_set_extesion_by_default("png")

    app = MyApp(0)

    from options import __PROGRAM_HOME__

    if not os.path.isdir(__PROGRAM_HOME__):
        try:
            os.mkdir(__PROGRAM_HOME__)
        except:
            pass

    logging.basicConfig(
        level=logging.INFO,
        filename=os.path.join(options.__PROGRAM_HOME__, "error.log"),
        filemode="a",
        format="%(asctime)s %(levelname)s %(message)s",
    )

    config.configure()

    dlg = StartDialog()
    if dlg.ShowModal() != wx.ID_OK:
        sys.exit(1)

    _conf = config.get("database")
    database.init(_conf)

    main_frame = ui.windows.main.main.MainFrame(_conf)
    app.SetTopWindow(main_frame)

    app.MainLoop()
