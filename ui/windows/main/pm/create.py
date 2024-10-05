import wx
import wx.adv

from pony.orm import *
from database import OrigSampleSet

from ui.icon import get_icon

WizPageChangingEvent, EVT_WIZ_PAGE_CHAGING = wx.lib.newevent.NewEvent()


class DialogCreatePmSeries(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetSize(350, 400)
        self.SetIcon(wx.Icon(get_icon("magic-wand")))
        self.SetTitle("Мастер добавления набора испытаний")
        self.CenterOnScreen()
        self._history = []
        self._pages = {
            "first": wx.Panel(self),
            "second": wx.Panel(self),
            "third": wx.Panel(self)
        }
        self._current_page_name = "first"
        self._calc_next_page_name()

        top_sizer = wx.BoxSizer(wx.VERTICAL)

        self._main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._deputy = wx.Panel(self)
        self._main_sizer.Add(self._deputy, 1, wx.EXPAND)
        line = wx.StaticLine(self)
        self._main_sizer.Add(line, 0, wx.EXPAND)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._btn_back = wx.Button(self, label="Назад")
        self._btn_back.Bind(wx.EVT_BUTTON, self._on_back)
        btn_sizer.Add(self._btn_back, 0, wx.EXPAND)
        self._btn_next = wx.Button(self, label="Далее")
        self._btn_next.SetDefault()
        self._btn_next.Bind(wx.EVT_BUTTON, self._on_next)
        btn_sizer.Add(self._btn_next, 0, wx.EXPAND)
        self._btn_cancel = wx.Button(self, wx.ID_CANCEL, label="Отмена")
        btn_sizer.Add(self._btn_cancel, 0, wx.EXPAND)
        self._main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, border=10)

        top_sizer.Add(self._main_sizer, 1, wx.EXPAND | wx.TOP, border=10)
        self.SetSizer(top_sizer)
        self.Layout()

        self._next_enabled = True

        self._update_controls_state()

    def _finalize(self):
        ...

    def _on_next(self, event):
        if self.is_last_page():
            self._finalize()
        else:
            self.go_next()

    def _on_back(self, event):
        self.go_back()

    def change_next_page(self, page_name):
        self._next_page_name = page_name
        self._update_controls_state()

    def _update_controls_state(self):
        self._btn_back.Enable(self.can_back())
        if self.is_last_page():
            label = "Завершить"
        else:
            label = "Далее"
        self._btn_next.SetLabelText(label)
        self._btn_next.Enable(self._next_enabled)

    def enable_next(self, enable=True):
        self._next_enabled = enable
        self._update_controls_state()

    def is_last_page(self):
        return self._next_page_name == None

    def can_back(self) -> bool:
        return len(self._history) > 0

    def _apply_current_page(self):
        page = self._pages[self._current_page_name]
        self._main_sizer.GetItem(0).GetWindow().Hide()
        self._main_sizer.Detach(0)
        self._main_sizer.Insert(0, page, 1, wx.EXPAND)
        page.Show()

    def _calc_next_page_name(self):
        names = list(self._pages.keys())
        if len(names) > names.index(self._current_page_name) + 1:
            self._next_page_name = names.__getitem__(
                names.index(self._current_page_name) + 1
            )
        else:
            self._next_page_name = None

    def go_next(self):
        if not self._next_enabled:
            return
        
        self._history.append(self._current_page_name)
        self._current_page_name = self._next_page_name
        self._calc_next_page_name()
        self._apply_current_page()
        self._update_controls_state()

    def go_back(self):
        if not self.can_back():
            return
        
        page_name = self._history.pop()
        self._current_page_name = page_name
        self._calc_next_page_name()
        self._apply_current_page()
        self._update_controls_state()