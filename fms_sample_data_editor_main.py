import logging
import os
import sys
import traceback

import wx

import config
import database
import options

import update.service
import version
from fms_sample_data_editor_ui.main.main import MainWindow
import ui.icon
from ui.start import StartDialog
import os


# Сообщаем PyInstaller, что загрузка завершена
if os.getenv("_PYI_SPLASH_IPC"):
    try:
        from pyi_splash import close  # type: ignore

        close()
    except:
        ...


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

    update.service.update_init("http://127.0.0.1:8000/", "geomech-fms-sample-data-editor", version.__GEOMECH_VERSION__, sys.executable)
    if update.service.update_check_status() == "AVAILABLE":
        rc = wx.MessageBox(
            "Доступно обновление для этой программы. Установить?",
            "Доступно обновление",
            style=wx.YES | wx.NO | wx.YES_DEFAULT | wx.ICON_INFORMATION,
        )
        if rc == wx.YES:
            update.service.update_patch_current_exe(None)

    dlg = StartDialog()
    if dlg.ShowModal() != wx.ID_OK:
        sys.exit(1)

    _conf = config.get("database")
    database.init(_conf)

    main_frame = MainWindow(_conf)
    app.SetTopWindow(main_frame)

    app.MainLoop()
