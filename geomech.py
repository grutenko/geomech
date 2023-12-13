# _*_ coding: UTF8 _*_

import wx
import sys, traceback
import database
from sqlalchemy.exc import SQLAlchemyError
import config
import traceback
import list_windows

def except_hook(exception_type, exception_value, exception_traceback):
    if exception_type is SQLAlchemyError:
        session = database.get_session()
        if session != None and session.in_transaction():
            session.rollback()

    message = 'Uncaught exception:\n'
    message += ''.join(traceback.format_exception(exception_type, exception_value, exception_traceback))
    print(message)

    dlg=wx.MessageDialog(None, "Ошибка: " + str(exception_value), str(exception_type), wx.OK|wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

sys.excepthook = except_hook

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = wx.App(0)

def _ask_dsn():
    while True:
        w = wx.TextEntryDialog(None, "URL базы данных", 'Доступ к БД')
        if w.ShowModal() != wx.ID_OK:
            exit()
        try:
            database.test_connection(w.GetValue())
        except (SQLAlchemyError, database.xDatabaseInitError) as e:
            except_hook(type(e), e, e.__traceback__)
        else:
            config.write_config('/Dsn', w.GetValue())
            break;

if __name__ == '__main__':
    config.init_config()

    try:
        database.test_connection(config.read_config('/Dsn'))
    except (SQLAlchemyError, database.xDatabaseInitError) as e:
        conn_success = False
        except_hook(type(e), e, e.__traceback__)
    else:
        conn_success = True

    if not conn_success or len(config.read_config('/Dsn')) == 0:
        _ask_dsn()
    try:
        database.init_database(config.read_config('/Dsn'))
    except (SQLAlchemyError, database.xDatabaseInitError) as e:
        config.write_config("/Dsn", "")
        raise e

    mainWindow = list_windows.cmd_show(database.DischargeMeasurement)
    app.SetTopWindow(mainWindow)
    app.MainLoop()

