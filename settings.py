from ui import Ui_Settings
import wx
from config import (
    read_config,
    write_config
)

class Settings(Ui_Settings):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.field_DatabaseUrl.SetValue(read_config("/DatabaseUrl"))

        self.button_SAVE.Bind(wx.EVT_BUTTON, self.__on_save_click)

    def __on_save_click(self, event):
        write_config("/DatabaseUrl", self.field_DatabaseUrl.GetValue())
        self.Close()