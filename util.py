import dialogs
import config
import wx
import database
from sqlalchemy.exc import SQLAlchemyError
import traceback
import logging

def except_hook(exception_type, exception_value, exception_traceback):
    if exception_type is SQLAlchemyError:
        session = database.get_session()
        if session != None and session.in_transaction():
            session.rollback()

    message = 'Uncaught exception:\n'
    message += ''.join(traceback.format_exception(exception_type, exception_value, exception_traceback))
    logging.exception(message)

    dlg=wx.MessageDialog(None, "Ошибка: " + str(exception_value), str(exception_type), wx.OK|wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


__DEFAULT_IP__ = '127.0.0.1'
__DEFAULT_PORT__ = 5432
__DEFAULT_NAME__ = 'geomech'

def ask_dsn(parent=None):
    while True:
        w = dialogs.DatabaseAccess(parent=parent)
        if config.has_option('database', 'user'):
            w.set_login_value(config.read_option('database', 'user'))
        w.set_ip_value(config.read_option('database', 'ip') if config.has_option('database', 'ip') else __DEFAULT_IP__)
        w.set_port_value(config.read_option('database', 'port') if config.has_option('database', 'port') else __DEFAULT_PORT__)
        w.set_name_value(config.read_option('database', 'name') if config.has_option('database', 'name') else __DEFAULT_NAME__)
        if w.ShowModal() != wx.ID_SAVE:
            return False
        try:
            database.test_connection(w.get_dsn())
        except (SQLAlchemyError, database.xDatabaseInitError) as e:
            except_hook(type(e), e, e.__traceback__)
        else:
            config.write_option('database', 'user', w.get_login()), 
            config.write_option('database', 'password', w.get_password()), 
            config.write_option('database', 'ip', w.get_ip()), 
            config.write_option('database', 'port', w.get_port()), 
            config.write_option('database', 'name', w.get_name())
            return True