import wx
import wx.adv

from pony.orm import *
from database import OrigSampleSet, MineObject, RockBurst
from ui.validators import *

from ui.icon import get_icon
from ui.datetimeutil import encode_datetime
from dateutil.parser import parse
from ui.datetimeutil import decode_datetime

WizPageChangingEvent, EVT_WIZ_PAGE_CHAGING = wx.lib.newevent.NewEvent()


class DialogCreateRockBurst(wx.Dialog):
    def __init__(self, parent, o=None, _type="CREATE"):
        super().__init__(parent, title="Добавить горный удар", size=wx.Size(400, 600))
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnScreen()

        self._type = _type
        if _type == "CREATE":
            ...
        else:
            self.SetTitle("Изменить: %s" % o.Name)
            self._target = o
        self.parent = None

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)

        label = wx.StaticText(self, label="Горный объект")
        main_sizer.Add(label, 0, wx.EXPAND)
        self.field_mine_object = wx.Choice(self)
        main_sizer.Add(self.field_mine_object, 0, wx.EXPAND | wx.BOTTOM, border=10)
        self.field_mine_object.Bind(wx.EVT_CHOICE, self._on_mine_object_changed)
        if self._type != "CREATE":
            self.field_mine_object.Disable()
        self._mine_objects = []

        @db_session
        def r(p=None):
            if p == None:
                objects = select(o for o in MineObject if o.Level == 0)
            else:
                objects = select(o for o in MineObject if o.parent == p)

            m = {
                "REGION": "Регион",
                "ROCKS": "Горный массив",
                "FIELD": "Месторождение",
                "HORIZON": "Горизонт",
                "EXCAVATION": "Выработка",
            }

            for o in objects:
                self.field_mine_object.Append((". " * o.Level) + "[" + m[o.Type] + "] " + o.Name)
                self._mine_objects.append(o)
                r(o)

        r()
        if len(self._mine_objects) > 0:
            self.field_mine_object.SetSelection(0)
            self.parent = self._mine_objects[0]

        if _type == "CREATE":
            autofill_sizer = wx.StaticBoxSizer(wx.VERTICAL, self, "Поля для автозаполнения")
            label = wx.StaticText(self, label="Наименование")
            autofill_sizer.Add(label, 0)
            self.field_orig_no = wx.TextCtrl(self, size=wx.Size(250, -1))
            self.field_orig_no.Bind(wx.EVT_KEY_UP, self._on_orig_no_updated)
            autofill_sizer.Add(self.field_orig_no, 0, wx.EXPAND)
            main_sizer.Add(autofill_sizer, 0, wx.EXPAND)

        label = wx.StaticText(
            self,
            label="Регистрационный номер " + ("(автом. из Наименование)*" if _type == "CREATE" else "*"),
        )
        main_sizer.Add(label, 0, wx.EXPAND | wx.TOP, border=10)
        self.field_number = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_number.SetValidator(TextValidator(lenMin=1, lenMax=32))
        main_sizer.Add(self.field_number, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(
            self,
            label="Название " + ("(автом. из Наименование)*" if _type == "CREATE" else "*"),
        )
        main_sizer.Add(label, 0)
        self.field_name = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_name.SetValidator(TextValidator(lenMin=1, lenMax=256))
        main_sizer.Add(self.field_name, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(
            self,
            label="Дата и время события",
        )
        main_sizer.Add(label, 0, wx.EXPAND | wx.TOP, border=10)
        self.field_burst_date = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_burst_date.SetValidator(DateValidator())
        main_sizer.Add(self.field_burst_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        collpane = wx.CollapsiblePane(self, wx.ID_ANY, "Комментарий")
        main_sizer.Add(collpane, 0, wx.GROW)

        comment_pane = collpane.GetPane()
        comment_sizer = wx.BoxSizer(wx.VERTICAL)
        comment_pane.SetSizer(comment_sizer)

        label = wx.StaticText(comment_pane, label="Комментарий")
        comment_sizer.Add(label, 0)
        self.field_comment = wx.TextCtrl(comment_pane, size=wx.Size(250, 100), style=wx.TE_MULTILINE)
        self.field_comment.SetValidator(TextValidator(lenMin=0, lenMax=512))
        comment_sizer.Add(self.field_comment, 0, wx.EXPAND | wx.BOTTOM, border=10)

        collpane = wx.CollapsiblePane(self, wx.ID_ANY, "Координаты")
        main_sizer.Add(collpane, 0, wx.GROW)

        coords_pane = collpane.GetPane()
        coords_sizer = wx.BoxSizer(wx.VERTICAL)
        coords_pane.SetSizer(coords_sizer)

        label = wx.StaticText(coords_pane, label="X (м)")
        coords_sizer.Add(label, 0)
        self.field_x = wx.SpinCtrlDouble(coords_pane, min=-100000000.0, max=10000000000.0)
        self.field_x.SetDigits(2)
        coords_sizer.Add(self.field_x, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(coords_pane, label="Y (м)")
        coords_sizer.Add(label, 0)
        self.field_y = wx.SpinCtrlDouble(coords_pane, min=-100000000.0, max=10000000000.0)
        self.field_y.SetDigits(2)
        coords_sizer.Add(self.field_y, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(coords_pane, label="Z (м)")
        coords_sizer.Add(label, 0)
        self.field_z = wx.SpinCtrlDouble(coords_pane, min=-100000000.0, max=10000000000.0)
        self.field_z.SetDigits(2)
        coords_sizer.Add(self.field_z, 0, wx.EXPAND | wx.BOTTOM, border=10)

        line = wx.StaticLine(self)
        main_sizer.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        if _type == "CREATE":
            label = "Создать"
        else:
            label = "Изменить"
        self.btn_save = wx.Button(self, label=label)
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        self.btn_save.SetDefault()
        btn_sizer.Add(self.btn_save, 0)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.TOP, border=10)

        self.SetSizer(top_sizer)

        self.Layout()
        self.Fit()

        if _type == "UPDATE":
            self._set_fields()

        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUP)

    def OnKeyUP(self, event):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    def _set_fields(self):
        mine_object = self._target.mine_object
        for index, o in enumerate(self._mine_objects):
            if o.RID == mine_object.RID:
                self.field_mine_object.SetSelection(index)
                break
        self.field_number.SetValue(self._target.Number)
        self.field_name.SetValue(self._target.Name)
        self.field_comment.SetValue(self._target.Comment)
        d = decode_datetime(self._target.BurstDate)
        self.field_burst_date.SetValue(
            "%s.%s.%s %s:%s:%s"
            % (str(d.day).zfill(2), str(d.month).zfill(2), str(d.year).zfill(4), str(d.hour).zfill(2), str(d.minute).zfill(2), str(d.second).zfill(2))
        )
        self.field_x.SetValue(self._target.X)
        self.field_y.SetValue(self._target.Y)
        self.field_z.SetValue(self._target.Z)

    def _on_mine_object_changed(self, event):
        self.parent = self._mine_objects[self.field_mine_object.GetSelection()]
        self._on_orig_no_updated()

    @db_session
    def _on_orig_no_updated(self, event=None):
        if event != None:
            event.Skip()
        if isinstance(self.parent, MineObject):
            parent = MineObject[self.parent.RID]
            name = str(self.field_orig_no.GetValue()) + " на"
            number = str(self.field_orig_no.GetValue())
        while parent.Level > 0:
            name += " " + parent.Name
            number += "@" + (parent.Name if len(parent.Name) < 4 else parent.Name[:4])
            parent = parent.parent

        self.field_name.SetValue(name)
        self.field_number.SetValue(number)

    @db_session
    def _on_save(self, event):
        if not self.Validate():
            return

        fields = {
            "mine_object": MineObject[self._mine_objects[self.field_mine_object.GetSelection()].RID],
            "Number": self.field_number.GetValue(),
            "Name": self.field_name.GetValue(),
            "Comment": self.field_comment.GetValue(),
            "X": self.field_x.GetValue(),
            "Y": self.field_y.GetValue(),
            "Z": self.field_z.GetValue(),
        }

        datetime = parse(self.field_burst_date.GetValue())
        date = wx.DateTime(datetime.day, datetime.month - 1, datetime.year)
        fields["BurstDate"] = encode_datetime(date, datetime.hour, datetime.minute, datetime.second)

        if self._type == "CREATE":
            self.o = RockBurst(**fields)
        else:
            o = RockBurst[self._target.RID]
            o.set(**fields)

        commit()
        self.EndModal(wx.ID_OK)
