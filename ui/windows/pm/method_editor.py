import wx
from pony.orm import commit, db_session, select
from pubsub import pub
from wx.adv import DP_ALLOWNONE, DP_DEFAULT, DP_SHOWCENTURY, DatePickerCtrl

from database import PmTestMethod
from ui.datetimeutil import decode_date, encode_date
from ui.icon import get_icon
from ui.validators import TextValidator


class PmMethodEditor(wx.Dialog):
    @db_session
    def __init__(self, parent, o=None, _type="CREATE"):
        super().__init__(parent, title="Добавить Метод испытаний", size=wx.Size(300, 400))
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()

        self._type = _type
        if _type == "CREATE":
            ...
        else:
            self.SetTitle("Изменить: %s" % o.Name)
            self._target = o

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, border=10)

        label = wx.StaticText(self, label="Название")
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

        label = wx.StaticText(self, label="Дата введения метода в действие*")
        main_sizer.Add(label, 0)
        self.field_start_date = DatePickerCtrl(self)
        main_sizer.Add(self.field_start_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата аннулирования метода")
        main_sizer.Add(label, 0)
        self.field_end_date = DatePickerCtrl(self, style=DP_DEFAULT | DP_SHOWCENTURY | DP_ALLOWNONE)
        main_sizer.Add(self.field_end_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        self.field_analytic = wx.CheckBox(self, label="Аналитический метод?")
        main_sizer.Add(self.field_analytic, 0, wx.EXPAND | wx.BOTTOM, border=10)

        line = wx.StaticLine(self)
        main_sizer.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        if _type == "CREATE":
            label = "Создать"
        else:
            label = "Изменить"
        self.btn_save = wx.Button(self, label=label)
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        btn_sizer.Add(self.btn_save, 0)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.TOP, border=10)

        self.SetSizer(top_sizer)

        self.Layout()
        self.Fit()

        if _type == "UPDATE":
            self._set_fields()

    @db_session
    def _on_save(self, event):
        if not self.Validate():
            return

        fields = {
            "Name": self.field_name.GetValue(),
            "Comment": self.field_comment.GetValue(),
            "Analytic": self.field_analytic.IsChecked(),
        }

        fields["StartDate"] = encode_date(self.field_start_date.GetValue())
        date: wx.DateTime = self.field_end_date.GetValue()
        if date.IsValid():
            fields["EndDate"] = encode_date(date)

        if self._type == "CREATE":
            o = PmTestMethod(**fields)
        else:
            o = PmTestMethod[self._target.RID]
            o.set(**fields)

        commit()
        self.o = o
        self.EndModal(wx.ID_OK)
        pub.sendMessage("object.added", o=o)

    def _set_fields(self):
        o = self._target
        self.field_name.SetValue(o.Name)
        self.field_comment.SetValue(o.Comment if o.Comment != None else "")
        self.field_start_date.SetValue(decode_date(o.StartDate))
        if o.EndDate != None:
            self.field_end_date.SetValue(decode_date(o.EndDate))
        self.field_analytic.Set3StateValue(wx.CHK_CHECKED if o.Analytic != None and o.Analytic else wx.CHK_UNCHECKED)
