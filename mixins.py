# _*_ coding: UTF8 _*_

import wx
import re
from typing import Dict

class OptionalFieldsMixin(object):
    _mapping: Dict[int, wx.Control] = {}
    _window = None

    def __init__(self, window) -> None:
        self._window = window
        for i, (key, checkbox) in enumerate(window.__dict__.items()):
            if re.match(r"field_(.+)_enabled", key):
                field = re.search(r"(.+)_enabled", key).group(1)
                if not field in window.__dict__:
                    raise Exception(u"Для чекбокса \"" + key + u"\" нет соотвествующего поля.")
                self._mapping[checkbox.GetId()] = field
                checkbox.Bind(wx.EVT_CHECKBOX, self.__on_toggle_optional_field_checkbox, id=checkbox.GetId())

    def __on_toggle_optional_field_checkbox(self, event: wx.Event):
        checkBox: wx.CheckBox = event.GetEventObject()
        if not checkBox.GetId() in self._mapping:
            return
        self._window.__dict__[ self._mapping[checkBox.GetId()] ].Enable( checkBox.IsChecked() )