import wx
from pony.orm import commit, db_session, select

from database import (
    PmProperty,
    PMSampleSet,
    PmSampleSetUsedProperties,
    PmTestEquipment,
    PmTestMethod,
)
from ui.delete_object import delete_object
from ui.icon import get_icon
from ui.validators import ChoiceValidator


class RecordEditor(wx.Dialog):
    @db_session
    def __init__(self, parent, pm_sample_set):
        super().__init__(parent, title="Добавить свойство", size=wx.Size(300, 400))
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()
        self.Layout()
        self.pm_sample_set = pm_sample_set
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, label="Свойство")
        sizer.Add(label, 0, wx.EXPAND)
        self.props = []
        self.field_prop = wx.Choice(self)
        self.field_prop.SetValidator(ChoiceValidator())
        used_props = list(map(lambda x: x.pm_property, select(o for o in PmSampleSetUsedProperties)))
        for p in select(o for o in PmProperty):
            if p not in used_props:
                self.props.append(p)
                self.field_prop.Append(p.Name)
        sizer.Add(self.field_prop, 0, wx.EXPAND | wx.BOTTOM, border=10)
        label = wx.StaticText(self, label="Метод")
        sizer.Add(label, 0, wx.EXPAND)
        self.field_method = wx.Choice(self)
        self.field_method.SetValidator(ChoiceValidator())
        self.methods = []
        for m in select(o for o in PmTestMethod):
            self.field_method.Append(m.Name)
            self.methods.append(m)
        sizer.Add(self.field_method, 0, wx.EXPAND | wx.BOTTOM, border=10)
        label = wx.StaticText(self, label="Оборудование")
        sizer.Add(label, 0, wx.EXPAND)
        self.equipment = []
        self.field_equipment = wx.Choice(self)
        self.field_equipment.SetValidator(ChoiceValidator())
        self.field_equipment.Append("Оборудование не требуется")
        self.equipment.append(None)
        for e in select(o for o in PmTestEquipment):
            self.equipment.append(e)
            self.field_equipment.Append(e.Name)
        self.field_equipment.SetSelection(0)
        sizer.Add(self.field_equipment, 0, wx.EXPAND | wx.BOTTOM, border=10)
        main_sizer.Add(sizer, 1, wx.EXPAND | wx.ALL, border=10)
        self.SetSizer(main_sizer)

        line = wx.StaticLine(self)
        main_sizer.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        self.btn_save = wx.Button(self, label="Добавить")
        self.btn_save.Bind(wx.EVT_BUTTON, self._on_save)
        self.btn_save.SetDefault()
        btn_sizer.Add(self.btn_save, 0)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, border=10)

        self.Layout()
        self.Fit()

    @db_session
    def _on_save(self, event):
        if not self.Validate():
            return

        fields = {
            "pm_sample_set": PMSampleSet[self.pm_sample_set.RID],
            "pm_property": PmProperty[self.props[self.field_prop.GetSelection()].RID],
            "pm_method": PmTestMethod[self.methods[self.field_method.GetSelection()].RID],
            "pm_equipment": (
                PmTestEquipment[self.equipment[self.field_equipment.GetSelection()].RID] if self.field_equipment.GetSelection() > 0 else None
            ),
        }

        o = PmSampleSetUsedProperties(**fields)
        commit()
        self.prop = self.props[self.field_prop.GetSelection()]
        self.method = self.methods[self.field_method.GetSelection()]
        self.equipment = self.equipment[self.field_equipment.GetSelection()]
        self.o = o
        self.EndModal(wx.ID_OK)


class GridSamplePropertiesDialog(wx.Dialog):
    def __init__(self, parent, pm_sample_set, on_prop_add, on_prop_remove):
        super().__init__(parent, title="Настроить свойства", size=wx.Size(800, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()

        self.pm_sample_set = pm_sample_set
        self._h_on_prop_add = on_prop_add
        self._h_on_prop_remove = on_prop_remove

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_HORZ_TEXT)
        item = self.toolbar.AddTool(wx.ID_ADD, "Добавить", get_icon("file-add"))
        self.toolbar.Bind(wx.EVT_TOOL, self._on_create, id=wx.ID_ADD)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_delete, id=wx.ID_DELETE)
        self.toolbar.AddSeparator()
        item = self.toolbar.AddTool(wx.ID_DELETE, "Удалить", get_icon("delete"))
        item.Enable(False)
        self.toolbar.Realize()
        sizer.Add(self.toolbar, 0, wx.EXPAND)

        self.list = wx.ListCtrl(self, style=wx.LC_REPORT)
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_item_selected)
        self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_item_deselected)
        self.list.AppendColumn("Название", width=150)
        self.list.AppendColumn("Метод испытаний", width=200)
        self.list.AppendColumn("Оборудование", width=200)
        sizer.Add(self.list, 1, wx.EXPAND)

        self.SetSizer(sizer)

        self.Layout()

        self.data = []
        self.load()

    def _on_item_selected(self, event):
        self.update_controls_state()

    def _on_item_deselected(self, event):
        self.update_controls_state()

    @db_session
    def load(self):
        self.list.DeleteAllItems()
        self.data = []
        for i, o in enumerate(select(o for o in PmSampleSetUsedProperties)):
            self.data.append(o)
            item = self.list.InsertItem(i, o.pm_property.Name)
            self.list.SetItem(item, 1, o.pm_method.Name)
            self.list.SetItem(item, 2, o.pm_equipment.Name if o.pm_equipment != None else "Не требуется")

    def _on_create(self, event):
        dlg = RecordEditor(self, self.pm_sample_set)
        if dlg.ShowModal() == wx.ID_OK:
            self._h_on_prop_add(dlg.prop, dlg.method, dlg.equipment)
            self.load()

    @db_session
    def _on_delete(self, event):
        index = self.list.GetFirstSelected()
        if index > -1:
            o = self.data[index]
            if delete_object(o, []):
                self._h_on_prop_remove(o.pm_property)
                self.load()

    def update_controls_state(self):
        self.toolbar.EnableTool(wx.ID_DELETE, self.list.GetSelectedItemCount() > 0)
