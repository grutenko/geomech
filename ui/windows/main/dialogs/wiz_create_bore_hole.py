import wx
import wx.lib.newevent
from pony.orm import *

from database import *
from ui.icon import get_icon

WizPageChangingEvent, EVT_WIZ_PAGE_CHAGING = wx.lib.newevent.NewEvent()


class WizCreateBoreHole(wx.Dialog):
    def __init__(self, parent, parent_o):
        super().__init__(parent)
        self.SetSize(350, 500)
        self.SetIcon(wx.Icon(get_icon("magic-wand")))
        self.SetTitle("Мастер добавления скважины")
        self.CenterOnScreen()
        self._history = []
        self._pages = {}
        self._apply_page0()
        self._apply_page1()
        self._apply_page2()
        self._current_page_name = "first"
        self._calc_next_page_name()

        self.parent_o = parent_o
        self.apply_parent_object()

        top_sizer = wx.BoxSizer(wx.VERTICAL)

        self._main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._deputy = wx.Panel(self)
        self._main_sizer.Add(self._pages["first"], 1, wx.EXPAND)
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

    def apply_parent_object(self):
        if self.parent_o != None:
            for i in range(self._field_parent.GetCount()):
                _o = self._field_parent.GetClientData(i)
                if isinstance(_o, type(self.parent_o)) and _o.RID == self.parent_o.RID:
                    self._field_parent.SetSelection(i)
                    break
            self._field_parent.Disable()

    @db_session
    def _apply_page0(self):
        panel = wx.Panel(self)
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)

        label = wx.StaticText(
            panel, label="Выбрите родительский горный объект или станцию"
        )
        main_sizer.Add(label, 0, wx.EXPAND)
        self._field_parent = wx.Choice(panel)
        self._field_parent.Bind(wx.EVT_CHOICE, self._on_orig_no_updated)
        main_sizer.Add(self._field_parent, 0, wx.EXPAND | wx.BOTTOM, border=10)

        mine_objects = {}
        for o in select(o for o in MineObject):
            mine_objects[o.RID] = o
        stations = {}
        for o in select(o for o in Station):
            stations[o.RID] = o
        m = {
            "REGION": "Регион",
            "ROCKS": "Горный массив",
            "FIELD": "Месторождение",
            "HORIZON": "Горизонт",
            "EXCAVATION": "Выработка",
        }

        def _r(p):
            for o in mine_objects.values():
                if o.parent == p:
                    self._field_parent.Append(
                        (". " * o.Level) + "[" + m[o.Type] + "]" + o.Name, o
                    )
                    _r(o)
            for o in stations.values():
                if o.mine_object == p:
                    self._field_parent.Append(
                        (". " * (p.Level + 1)) + "[Станция]" + o.Name, o
                    )
                    _r(o)

        _r(None)
        self._field_parent.Update()

        panel.SetSizer(top_sizer)
        panel.Layout()

        self._pages["first"] = panel

    def _apply_page1(self):
        panel = wx.Panel(self)
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)

        label = wx.StaticText(panel, label="Номер скважины")
        main_sizer.Add(label, 0, wx.EXPAND)
        self._field_number = wx.TextCtrl(panel)
        self._field_number.Bind(wx.EVT_KEY_UP, self._on_orig_no_updated)
        main_sizer.Add(self._field_number, 0, wx.EXPAND)
        self.label_exists = wx.StaticText(
            panel, label="Скважина с таким названием уже существует"
        )
        self.label_exists.SetForegroundColour(wx.Colour(238, 75, 43))
        self.label_exists.Hide()
        main_sizer.Add(self.label_exists, 0, wx.EXPAND)
        self.label_number = wx.StaticText(panel, label="№: ")
        self.label_number.SetForegroundColour(wx.Colour(100, 100, 100))
        main_sizer.Add(self.label_number, 0, wx.EXPAND)
        self.label_name = wx.StaticText(panel, label="Название: ")
        self.label_name.SetForegroundColour(wx.Colour(100, 100, 100))
        main_sizer.Add(self.label_name, 0, wx.EXPAND | wx.BOTTOM, border=10)
        self._on_orig_no_updated()
        label = wx.StaticText(panel, label="Комментарий")
        main_sizer.Add(label, 0)
        self.field_comment = wx.TextCtrl(
            panel, size=wx.Size(250, 100), style=wx.TE_MULTILINE
        )
        main_sizer.Add(self.field_comment, 0, wx.EXPAND | wx.BOTTOM, border=10)
        label = wx.StaticText(panel, label="Дата закладки скважины / начала измерений*")
        main_sizer.Add(label, 0)
        self.field_start_date = wx.TextCtrl(panel)
        main_sizer.Add(self.field_start_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(panel, label="Дата завершения измерений")
        main_sizer.Add(label, 0)
        self.field_end_date = wx.TextCtrl(panel)
        main_sizer.Add(self.field_end_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(panel, label="Дата ликвидации скважины")
        main_sizer.Add(label, 0)
        self.field_destroy_date = wx.TextCtrl(panel)
        main_sizer.Add(self.field_destroy_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        panel.SetSizer(top_sizer)
        panel.Layout()
        panel.Hide()

        self._pages["second"] = panel

    def _apply_page2(self):
        panel = wx.Panel(self)
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)

        label = wx.StaticText(panel, label="Азимут (град.)")
        main_sizer.Add(label, 0)
        self.field_azimuth = wx.SpinCtrlDouble(
            panel, min=-100000000.0, max=10000000000.0
        )
        self.field_azimuth.SetDigits(2)
        main_sizer.Add(self.field_azimuth, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(panel, label="Наклон (град.)")
        main_sizer.Add(label, 0)
        self.field_tilt = wx.SpinCtrlDouble(panel, min=-100000000.0, max=10000000000.0)
        self.field_tilt.SetDigits(2)
        main_sizer.Add(self.field_tilt, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(panel, label="Диаметр (м)")
        main_sizer.Add(label, 0)
        self.field_diameter = wx.SpinCtrlDouble(
            panel, min=-100000000.0, max=10000000000.0
        )
        self.field_diameter.SetDigits(2)
        main_sizer.Add(self.field_diameter, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(panel, label="Длина (м)")
        main_sizer.Add(label, 0)
        self.field_length = wx.SpinCtrlDouble(
            panel, min=-100000000.0, max=10000000000.0
        )
        self.field_length.SetDigits(2)
        main_sizer.Add(self.field_length, 0, wx.EXPAND | wx.BOTTOM, border=10)

        panel.SetSizer(top_sizer)
        panel.Layout()
        panel.Hide()

        self._pages["third"] = panel

    @db_session
    def _on_orig_no_updated(self, event=None):
        if event != None:
            event.Skip()
        if self._field_parent.GetSelection() == -1:
            return
        p = self._field_parent.GetClientData(self._field_parent.GetSelection())
        if isinstance(p, MineObject):
            parent = MineObject[p.RID]
            name = str(self._field_number.GetValue()) + " на"
            number = str(self._field_number.GetValue())
        else:
            station = Station[p.RID]
            parent = station.mine_object
            name = (
                station.Number.split("@")[0]
                + "/"
                + str(self._field_number.GetValue())
                + " на"
            )
            number = (
                str(self._field_number.GetValue()) + "@" + station.Number.split("@")[0]
            )
        while parent.Level > 0:
            name += " " + parent.Name
            number += "@" + (parent.Name if len(parent.Name) < 4 else parent.Name[:4])
            parent = parent.parent

        self.label_name.SetLabelText("Название: " + name)
        self.label_number.SetLabelText("№: " + number)
        self._validate_name(name)

    @db_session
    def _validate_name(self, name):
        self.label_exists.Show(
            select(o for o in BoreHole if o.Name == name).count() > 0
        )

    def _finalize(self): ...

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
        page.Layout()
        self.Layout()

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
