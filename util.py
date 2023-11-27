import wx
import threading
import time
from database import (
    get_session
)
from queue import Queue

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
    w = wx.ProgressDialog("Обновление", "Идет обновление базы данных...", style=wx.PD_AUTO_HIDE, parent=parent)
    while True:
        time.sleep(0.01)
        if not exc_bucket.empty():
            w.Update(100)
            w.Close()
            raise exc_bucket.get(False)
        w.Pulse()
        if not t.is_alive():
            break;
    w.Update(100)
    w.Close()