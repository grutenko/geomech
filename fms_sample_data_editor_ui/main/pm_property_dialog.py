import wx

from pony.orm import select, db_session, commit
from database import PmProperty, PmTestEquipment, PmTestMethod, PmSamplePropertyValue, PMSample
from ui.icon import get_icon
from ui.validators import ChoiceValidator


class PmPropertyDialog(wx.Dialog):
    @db_session
    def __init__(self, parent, pm_sample):
        super().__init__(parent)
        self.pm_sample = pm_sample

        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()
        self.Layout()
        self.pm_sample = pm_sample
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, label="Свойство")
        sizer.Add(label, 0, wx.EXPAND)
        self.props = []
        self.field_prop = wx.Choice(self)
        self.field_prop.SetValidator(ChoiceValidator())
        self.native_props = []
        if pm_sample.Length1 is None:
            self.field_prop.Append("Сторона 1")
            self.native_props.append("Length1")
        if pm_sample.Length2 is None:
            self.field_prop.Append("Сторона 2")
            self.native_props.append("Length2")
        if pm_sample.Height is None:
            self.field_prop.Append("Высота")
            self.native_props.append("Height")
        if pm_sample.MassAirDry is None:
            self.field_prop.Append("Масса в воздушно сухом состоянии")
            self.native_props.append("MassAirDry")
        self.field_prop.Bind(wx.EVT_CHOICE, self.on_select_property)
        used_props = list(map(lambda x: x.pm_property, select(o for o in PmSamplePropertyValue if o.pm_sample == pm_sample)))
        for p in select(o for o in PmProperty):
            if p not in used_props:
                self.props.append(p)
                self.field_prop.Append(p.Name)
        if self.field_prop.GetCount() > 0:
            self.field_prop.SetSelection(0)
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
        self.btn_save.Bind(wx.EVT_BUTTON, self.on_save)
        self.btn_save.SetDefault()
        btn_sizer.Add(self.btn_save, 0)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, border=10)

        self.Layout()
        self.Fit()
        self.update_controls_state()

    def on_select_property(self, event):
        self.update_controls_state()

    def update_controls_state(self):
        self.field_method.Enable(self.field_prop.GetSelection() >= len(self.native_props))
        self.field_equipment.Enable(self.field_prop.GetSelection() >= len(self.native_props))

    @db_session
    def on_save(self, event):
        if not self.Validate():
            return

        if self.field_prop.GetSelection() < len(self.native_props):
            setattr(PMSample[self.pm_sample.RID], self.native_props[self.field_prop.GetSelection()], 0.0)
        else:
            fields = {}
            fields["pm_sample"] = PMSample[self.pm_sample.RID]
            fields["pm_test_method"] = self.methods[self.field_method.GetSelection()]
            fields["pm_property"] = self.props[self.field_prop.GetSelection() - 4]
            fields["Value"] = 0.0
            o = PmSamplePropertyValue(fields)

        commit()
        self.EndModal(wx.ID_OK)
