import wx
from main_window import MainWindow
from database import init
import sys, traceback
import sqlalchemy
from database import get_session
import config
import traceback

def my_message(exception_type, exception_value, exception_traceback):
    if exception_type is sqlalchemy.exc.SQLAlchemyError:
        session = get_session()
        if session != None and session.in_transaction():
            session.rollback()

    message = 'Uncaught exception:\n'
    message += ''.join(traceback.format_exception(exception_type, exception_value, exception_traceback))
    print(message)

    dlg=wx.MessageDialog(None, "Ошибка: " + str(exception_value), str(exception_type), wx.OK|wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

sys.excepthook = my_message

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

app = wx.App(0)

def _ask_dsn():
    while True:
        w = wx.TextEntryDialog(None, "URL базы данных", 'Доступ к БД')
        if w.ShowModal() == wx.ID_OK:
            try:
                init(w.GetValue())
            except Exception as e:
                my_message(type(e), e, e.__traceback__)
            else:
                config.write_config('/DatabaseUrl', w.GetValue())
                break;
        else:
            exit()

if __name__ == '__main__':
    config.init_config()
    config.write_config('/DatabaseUrl', "")
    if len(config.read_config('/DatabaseUrl')) == 0:
        _ask_dsn()
    init(config.read_config('/DatabaseUrl'))
    mainWindow = MainWindow(None)
    mainWindow.Show()
    app.SetTopWindow(mainWindow)
    app.MainLoop()

