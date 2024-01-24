import dialogs
import wx
from database import Credentials, validate_credentials
import traceback
import logging

def show_exception(e: Exception):
    message = 'Uncaught exception:\n'
    message += ''.join(traceback.format_exception(e.__class__, e, e.__traceback__))
    logging.exception(message)

    dlg=wx.MessageDialog(None, "Ошибка: " + str(e), str(e.__class__), wx.OK|wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

def ask_credentials(credentials: Credentials = None, parent=None) -> Credentials:
    while True:
        w = dialogs.DatabaseAccess(parent=parent)
        if credentials != None:
            w.setCredentials(credentials)
        if w.ShowModal() != wx.ID_SAVE:
            return None
        credentials = w.getCredentials()
        try:
            validate_credentials(credentials)
        except Exception as e:
            show_exception(e)
        else:
            return credentials
    
    return credentials