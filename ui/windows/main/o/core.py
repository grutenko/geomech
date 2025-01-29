import wx
import wx.adv
from pony.orm import commit, db_session

import ui.datetimeutil
from database import BoreHole, MineObject, OrigSampleSet
from ui.icon import get_icon
from ui.validators import DateValidator, TextValidator


class DialogCreateCore(wx.Dialog):
    @db_session
    def __init__(self, parent, o=None, _type="CREATE"):
        super().__init__(parent, title="Добавить Керн", size=wx.Size(400, 600))
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()

        self._type = _type
        if _type == "CREATE":
            self.parent = o
        else:
            self.SetTitle("Изменить: %s" % o.Name)
            self._target = o
            self.parent = MineObject[o.mine_object.RID] if o.bore_hole == None else BoreHole[o.bore_hole.RID]

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)

        label = wx.StaticText(self, label="Регистрационный номер*")
        main_sizer.Add(label, 0, wx.EXPAND)
        self.field_number = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_number.SetValidator(TextValidator(lenMin=1, lenMax=32))
        main_sizer.Add(self.field_number, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Название*")
        main_sizer.Add(label, 0)
        self.field_name = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_name.SetValidator(TextValidator(lenMin=1, lenMax=256))
        main_sizer.Add(self.field_name, 0, wx.EXPAND | wx.BOTTOM, border=10)

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

        label = wx.StaticText(self, label="Дата начала отбора образцов*")
        main_sizer.Add(label, 0)
        self.field_start_date = wx.TextCtrl(self)
        self.field_start_date.SetValidator(DateValidator())
        main_sizer.Add(self.field_start_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата завершения отбора")
        main_sizer.Add(label, 0)
        self.field_end_date = wx.TextCtrl(self)
        self.field_start_date.SetValidator(DateValidator(allow_empty=True))
        main_sizer.Add(self.field_end_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        line = wx.StaticLine(self)
        main_sizer.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        if _type == "CREATE":
            label = "Создать"
        else:
            label = "Изменить"
        self.btn_save = wx.Button(self, label=label)
        self.btn_save.SetDefault()
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        btn_sizer.Add(self.btn_save, 0)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.TOP, border=10)

        self.SetSizer(top_sizer)

        self.Layout()
        self.Fit()

        if _type == "UPDATE":
            self._set_fields()
        else:
            self._apply_fields()

        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUP)

    def OnKeyUP(self, event):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    def _set_fields(self):
        o = self._target
        self.field_number.SetValue(o.Number)
        self.field_name.SetValue(o.Name)
        self.field_comment.SetValue(o.Comment if o.Comment != None else "")
        self.field_start_date.SetValue(ui.datetimeutil.decode_date(o.StartSetDate).__str__())
        if o.EndSetDate != None:
            self.field_end_date.SetValue(ui.datetimeutil.decode_date(o.EndSetDate).__str__())

    def _apply_fields(self):
        self.field_name.SetValue("Керн:" + self.parent.Name)
        self.field_number.SetValue("Керн:" + self.parent.Number)
        self.field_start_date.SetValue(str(ui.datetimeutil.decode_date(self.parent.StartDate)))
        if self.parent.StartDate != None:
            self.field_end_date.SetValue(str(ui.datetimeutil.decode_date(self.parent.EndDate)))

    @db_session
    def _on_save(self, event):
        if not self.Validate():
            return

        fields = {
            "Number": self.field_number.GetValue(),
            "Name": self.field_name.GetValue(),
            "Comment": self.field_comment.GetValue(),
            "X": self.parent.X,
            "Y": self.parent.Y,
            "Z": self.parent.Z,
            "SampleType": "CORE",
        }

        if self._type == "CREATE":
            fields["mine_object"] = MineObject[self.parent.mine_object.RID]
            fields["bore_hole"] = BoreHole[self.parent.RID]

        fields["StartSetDate"] = ui.datetimeutil.encode_date(self.field_start_date.GetValue())

        date = self.field_end_date.GetValue()
        if len(date.strip()) > 0:
            fields["EndSetDate"] = ui.datetimeutil.encode_date(date)

        if self._type == "CREATE":
            self.o = OrigSampleSet(**fields)
        else:
            self.o = OrigSampleSet[self._target.RID]
            self.o.set(**fields)

        commit()
        self.EndModal(wx.ID_OK)
