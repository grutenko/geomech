import wx
import threading
import time
from database import (
    get_session
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from queue import Queue
from config import read_config
import traceback


def commit_changes(parent):
    def _thread(exc_bucket):
        try:
            get_session().commit()
        except Exception as e:
            get_session().rollback()
            exc_bucket.put(e)

    exc_bucket = Queue()
    t = threading.Thread(target=_thread, args=[exc_bucket])
    t.start()
    w = wx.ProgressDialog("Обновление", "Идет обновление базы данных...", style=0, parent=parent)
    while True:
        if not t.is_alive():
            if not exc_bucket.empty():
                w.Destroy()
                raise exc_bucket.get(False)
            else:
                break
        else:
            time.sleep(0.01)
            w.Pulse()
    w.Destroy()

def except_hook(exception_type, exception_value, exception_traceback):
    if exception_type is SQLAlchemyError:
        session = get_session()
        if session != None and session.in_transaction():
            session.rollback()

    message = 'Uncaught exception:\n'
    message += ''.join(traceback.format_exception(exception_type, exception_value, exception_traceback))
    print(message)

    dlg=wx.MessageDialog(None, "Ошибка: " + str(exception_value), str(exception_type), wx.OK|wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

def ask_dsn() -> str:
    while True:
        w = wx.TextEntryDialog(None, "URL базы данных", 'Доступ к БД')
        if w.ShowModal() != wx.ID_OK:
            return None
        try:
            session = Session(bind=create_engine(w.GetValue()))
        except SQLAlchemyError as e:
            except_hook(type(e), e, e.__traceback__)
        else:
            session.close()
            return w.GetValue()