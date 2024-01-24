# _*_ coding: UTF8 _*_

from ui import Ui_Settings
import wx
import config
import util

class Settings(Ui_Settings):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.button_SAVE.Bind(wx.EVT_BUTTON, self.__on_save_click)
        self.btn_edit_database_access.Bind(wx.EVT_BUTTON, self.__on_edit_database_access)

    def __on_save_click(self, event):
        self.Close()

    def __on_edit_database_access(self, event):
        c = util.ask_credentials(config.read_database_credentials(), parent=self)
        if c != None:
            config.write_database_credentials(c)