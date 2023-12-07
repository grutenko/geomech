# _*_ coding: UTF8 _*_

from ui import Ui_Settings
import wx
import config
import database
from sqlalchemy.exc import SQLAlchemyError

class DsnValidator(wx.Validator):
    def TransferToWindow(self):
        return True
    
    def TransferFromWindow(self):
        return True
    
    def Validate(self, parent):
        ctrl: wx.Control = self.GetWindow()
        dsn = ctrl.GetValue()
        try:
            database.test_connection(dsn)
        except (SQLAlchemyError, database.xDatabaseInitError) as e:
            dlg=wx.MessageDialog(None, "Ошибка: " + str(e), str(type(e)), wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            ctrl.SetBackgroundColour("red")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False
        else:
            ctrl.SetBackgroundColour(
                 wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            ctrl.Refresh()
            return True
    
    def Clone(self):
        return DsnValidator()

class Settings(Ui_Settings):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.field_DatabaseUrl.SetValue(config.read_config("/Dsn"))

        self.button_SAVE.Bind(wx.EVT_BUTTON, self.__on_save_click)

        self.field_DatabaseUrl.SetValidator(DsnValidator())

    def __on_save_click(self, event):
        if not self.Validate():
            return
        config.write_config("/Dsn", self.field_DatabaseUrl.GetValue())
        self.Close()