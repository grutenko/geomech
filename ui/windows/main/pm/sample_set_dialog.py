import wx
from pony.orm import *
from pubsub import pub

from database import *
from ui.datetimeutil import decode_date, encode_date
from ui.icon import get_icon
from ui.validators import *


class ComboBoxWithSuggesion(wx.ComboBox):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self._synthetic_text_enter = False
        self.suggested = False

        self.Bind(wx.EVT_CHAR, self._on_char)
        self.Bind(wx.EVT_TEXT, self._on_text)

    def _on_char(self, event: wx.KeyEvent):
        _from, _to = self.GetTextSelection()
        if event.GetKeyCode() == wx.WXK_BACK and abs(_from - _to) > 0:
            self.SetTextSelection(max(_from - 1, 0), _to)
        event.Skip()

    def _on_text(self, event):
        self.suggested = False
        if self._synthetic_text_enter:
            return
        self._synthetic_text_enter = True
        _text = event.GetString()
        _found = False
        if len(_text) == 0:
            self.SetValue("")
            self._synthetic_text_enter = False
            return

        for index, choice in enumerate(self.GetItems()):
            if choice.upper().startswith(_text.upper()):
                self.suggested = True
                self.SetValue(choice)
                self.SetInsertionPoint(len(_text))
                self.SetTextSelection(len(_text), len(choice))
                _found = True
                break
        if _found:
            event.Skip()

        self._synthetic_text_enter = False


class SampleSetDialog(wx.Dialog):
    @db_session
    def __init__(self, parent, o=None, _type="CREATE"):
        super().__init__(parent, title="Добавить пробу", size=wx.Size(400, 300))
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnScreen()

        self._type = _type
        if _type == "CREATE":
            self.parent = o
        else:
            self.SetTitle("Изменить: %s" % o.Name)
            self._target = o
            self.parent = PMTestSeries[o.pm_test_series.RID]

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

        label = wx.StaticText(self, label="Горный объект")
        main_sizer.Add(label, 0)
        self.field_mine_object = wx.Choice(self)
        main_sizer.Add(self.field_mine_object, 0, wx.EXPAND | wx.BOTTOM, border=10)

        self._mine_objects = list(select(o for o in MineObject if o.Type == "FIELD"))
        for o in self._mine_objects:
            self.field_mine_object.Append(o.Name)

        if len(self._mine_objects) > 0:
            self.field_mine_object.SetSelection(0)

        label = wx.StaticText(self, label="Дата отбора")
        main_sizer.Add(label, 0)
        self.field_set_date = wx.TextCtrl(self)
        self.field_set_date.SetValidator(DateValidator(allow_empty=True))
        main_sizer.Add(self.field_set_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Дата испытания")
        main_sizer.Add(label, 0)
        self.field_test_date = wx.TextCtrl(self)
        self.field_test_date.SetValidator(DateValidator(allow_empty=True))
        main_sizer.Add(self.field_test_date, 0, wx.EXPAND | wx.BOTTOM, border=10)

        self.field_real_details = wx.CheckBox(self, label="Реальные данные?")
        main_sizer.Add(self.field_real_details, 0, wx.EXPAND | wx.BOTTOM, border=10)

        label = wx.StaticText(self, label="Петротип")
        main_sizer.Add(label, 0)
        self.field_petrotype = ComboBoxWithSuggesion(self)
        self.field_petrotype.Bind(wx.EVT_COMBOBOX, self._on_select_petrotype)
        self.field_petrotype.Bind(wx.EVT_TEXT, self._on_select_petrotype)
        main_sizer.Add(self.field_petrotype, 0, wx.EXPAND | wx.BOTTOM, border=10)

        self._petrotypes = list(select(o for o in Petrotype))
        for _o in self._petrotypes:
            self.field_petrotype.Append(_o.Name)

        label = wx.StaticText(self, label="Структура петротипа")
        main_sizer.Add(label, 0)
        self._petrotype_structs = []
        self.field_petrotype_struct = ComboBoxWithSuggesion(self)
        main_sizer.Add(self.field_petrotype_struct, 0, wx.EXPAND | wx.BOTTOM, border=10)

        if len(self._petrotypes) > 0:
            self.field_petrotype.SetSelection(0)
            self._on_select_petrotype()

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

    @db_session
    def _on_select_petrotype(self, event=None):
        _text = self.field_petrotype.GetValue()
        _petrotype = select(o for o in Petrotype if o.Name.lower() == _text.lower()).first()
        if _petrotype != None:
            _petrotype_structs = select(o for o in PetrotypeStruct if o.petrotype == _petrotype)
            self._petrotype_structs = _petrotype_structs
            self.field_petrotype_struct.Clear()
            for o in _petrotype_structs:
                self.field_petrotype_struct.Append(o.Name)
            if len(_petrotype_structs) > 0:
                self.field_petrotype_struct.SetSelection(0)
        if event != None:
            event.Skip()

    @db_session
    def _on_save(self, event):
        if not self.Validate():
            return

        fields = {"Number": self.field_name.GetValue(), "Comment": self.field_comment.GetValue()}
        fields["mine_object"] = MineObject[self._mine_objects[self.field_mine_object.GetSelection()].RID]
        fields["pm_test_series"] = PMTestSeries[self.parent.RID]
        if len(self.field_set_date.GetValue()) > 0:
            fields["SetDate"] = encode_date(self.field_set_date.GetValue())
        if len(self.field_set_date.GetValue()) > 0:
            fields["TestDate"] = encode_date(self.field_test_date.GetValue())
        fields["RealDetails"] = self.field_real_details.IsChecked()

        _petrotype_name = self.field_petrotype.GetValue().lower()
        _petrotype_struct_name = self.field_petrotype_struct.GetValue().lower()
        _petrotype = select(o for o in Petrotype if o.Name.lower() == _petrotype_name).first()
        if _petrotype == None:
            _petrotype = Petrotype(Name=_petrotype)
            _petrotype_struct = PetrotypeStruct(Name=_petrotype_struct_name, petrotype=_petrotype)
        else:
            _petrotype_struct = select(o for o in PetrotypeStruct if o.Name.lower() == _petrotype_struct_name).first()
            if _petrotype_struct == None:
                _petrotype_struct = PetrotypeStruct(Name=_petrotype_struct_name, petrotype=_petrotype)

        fields["petrotype_struct"] = _petrotype_struct

        if self._type == "CREATE":
            o = PMSampleSet(**fields)
        else:
            o = PMSampleSet[self._target.RID]
            o.set(**fields)

        commit()
        self.o = o
        self.EndModal(wx.ID_OK)
        if self._type == "CREATE":
            pub.sendMessage("object.added", o=o)
        else:
            pub.sendMessage("object.updated", o=o)

    @db_session
    def _set_fields(self):
        o = self._target
        self.field_name.SetValue(o.Name)
        self.field_comment.SetValue(o.Comment if o.Comment != None else "")
        for index, _o in enumerate(self._mine_objects):
            if _o.RID == o.mine_object.RID:
                self.field_mine_object.SetSelection(index)
                break
        if o.SetDate != None:
            self.field_set_date.SetValue(decode_date(o.SetDate))
        if o.TestDate != None:
            self.field_test_date.SetValue(decode_date(o.TestDate))

        if o.RealDetails:
            self.field_real_details.SetValue(True)

        _struct = PetrotypeStruct[o.petrotype_struct.RID]

        for i, _p in enumerate(self._petrotypes):
            if _p.RID == _struct.petrotype.RID:
                self.field_petrotype.SetSelection(i)
                self._on_select_petrotype()

        for i, _p in enumerate(self._petrotype_structs):
            if _p.RID == _struct.RID:
                self.field_petrotype_struct.SetSelection(i)
