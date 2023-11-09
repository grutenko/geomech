import wx
from MainWindow import MainWindow
from sqlalchemy import (
    create_engine,
)
from sqlalchemy.orm import sessionmaker
from database import initDatabase
import sys, traceback

def my_message(exception_type, exception_value, exception_traceback):
    message = 'Uncaught exception:\n'
    message += ''.join(traceback.format_exception(type, exception_value, exception_traceback))
    print(message)

    dlg=wx.MessageDialog(None, "Ошибка: " + str(exception_value), str(exception_type), wx.OK|wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

sys.excepthook = my_message

'''import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
'''
app = wx.App(0)

if __name__ == '__main__':
    initDatabase('postgresql://aleksejfedorenko@localhost/aleksejfedorenko')
    mainWindow = MainWindow(None)
    mainWindow.Show()
    app.SetTopWindow(mainWindow)
    app.MainLoop()
