import wx
import wx.adv
from wx.adv import DatePickerCtrl, DP_ALLOWNONE, DP_DEFAULT, DP_SHOWCENTURY

from ui.validators import *
from database import *
import ui.datetimeutil


class DialogCreateCore(wx.Dialog):
    def __init__(self, parent, o=None):
        super().__init__(parent, title="Добавить Керн", size=wx.Size(400, 600))
        self.SetIcon(wx.Icon("./icons/logo@16.jpg"))

        self.parent = o

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

        label = wx.StaticText(self, label="Комментарий")
        main_sizer.Add(label, 0)
        self.field_comment = wx.TextCtrl(
            self, size=wx.Size(250, 100), style=wx.TE_MULTILINE
        )
        self.field_comment.SetValidator(TextValidator(lenMin=0, lenMax=512))
        main_sizer.Add(self.field_comment, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата начала отбора образцов*")
        main_sizer.Add(label, 0)
        self.field_start_date = DatePickerCtrl(self)
        main_sizer.Add(self.field_start_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата завершения отбора")
        main_sizer.Add(label, 0)
        self.field_end_date = DatePickerCtrl(
            self, style=DP_DEFAULT | DP_SHOWCENTURY | DP_ALLOWNONE
        )
        main_sizer.Add(self.field_end_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        line = wx.StaticLine(self)
        main_sizer.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        self.btn_save = wx.Button(self, label="Создать")
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        btn_sizer.Add(self.btn_save, 0)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.TOP, border=10)

        self.SetSizer(top_sizer)

        self.Layout()
        self.Fit()

        self._apply_fields()

    def _apply_fields(self):
        self.field_name.SetValue("Керн:" + self.parent.Name)
        self.field_number.SetValue("Керн:" + self.parent.Number)

    @db_session
    def _on_save(self, event):
        if not self.Validate():
            return
        
        fields = {
            "Number": self.field_number.GetValue(),
            "Name": self.field_name.GetValue(),
            'Comment': self.field_comment.GetValue(),
            'X': self.parent.X,
            'Y': self.parent.Y,
            'Z': self.parent.Z,
            'SampleType': 'CORE',
            'mine_object': MineObject[self.parent.mine_object.RID],
            'bore_hole': BoreHole[self.parent.RID]
        }

        fields["StartSetDate"] = ui.datetimeutil.encode_date(
            self.field_start_date.GetValue()
        )

        date: wx.DateTime = self.field_end_date.GetValue()
        if date.IsValid():
            fields["EndSetDate"] = ui.datetimeutil.encode_date(date)

        try:
            self.o = OrigSampleSet(**fields)
        except Exception as e:
            wx.MessageBox(str(e))
        else:
            self.EndModal(wx.ID_OK)