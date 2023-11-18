import wx
from main_window import MainWindow
from sqlalchemy.orm import sessionmaker
from database import init
import sys, traceback
import sqlalchemy
from database import get_session

def my_message(exception_type, exception_value, exception_traceback):
    if exception_type is sqlalchemy.exc.SQLAlchemyError:
        session = get_session()
        if session != None and session.in_transaction():
            session.rollback()

    message = 'Uncaught exception:\n'
    message += ''.join(traceback.format_exception(type, exception_value, exception_traceback))
    print(message)

    dlg=wx.MessageDialog(None, "Ошибка: " + str(exception_value), str(exception_type), wx.OK|wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

sys.excepthook = my_message

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

app = wx.App(0)

if __name__ == '__main__':
    init('postgresql://aleksejfedorenko@localhost/aleksejfedorenko')
    mainWindow = MainWindow(None)
    mainWindow.Show()
    app.SetTopWindow(mainWindow)
    app.MainLoop()
