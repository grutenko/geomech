import wx
from pony.orm import *
from pubsub import pub

from database import PmProperty, PmPropertyClass
from ui.icon import get_icon
from ui.validators import TextValidator


class PmPropertyEditor(wx.Dialog):
    @db_session
    def __init__(self, parent, o=None, _type="CREATE"):
        super().__init__(parent, title="Добавить свойство", size=wx.Size(300, 400))
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

        label = wx.StaticText(self, label="Класс")
        main_sizer.Add(label, 0)
        self.field_class = wx.Choice(self)
        self._classes = []
        for o in select(o for o in PmPropertyClass):
            self.field_class.Append(o.Name)
            self._classes.append(o)
        main_sizer.Add(self.field_class, 0, wx.EXPAND | wx.BOTTOM, border=10)

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

        if self.field_class.GetSelection() == -1:
            wx.MessageBox("Не выбран класс", "Ошибка")
            return
        _class = self._classes[self.field_class.GetSelection()]
        _fields = {
            "pm_property_class": PmPropertyClass[_class.RID],
            "Name": self.field_name.GetValue(),
            "Comment": self.field_comment.GetValue(),
        }
        if self._type == "CREATE":
            o = PmProperty(**_fields)
        else:
            o = PmProperty[self._target.RID]
            o.set(**_fields)
        commit()
        self.o = o
        self.EndModal(wx.ID_OK)
        pub.sendMessage("object.added", o=o)

    def _set_fields(self):
        for index, _class in enumerate(self._classes):
            if _class.RID == self._target.pm_property_class.RID:
                self.field_class.SetSelection(index)
                break
        self.field_name.SetValue(self._target.Name)
        self.field_comment.SetValue(self._target.Comment if self._target.Comment != None else "")
