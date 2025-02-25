import wx
import wx.propgrid
from ui.icon import get_icon

from database import PMSample, PmSamplePropertyValue
from pony.orm import db_session, select, commit
from .pm_property_dialog import PmPropertyDialog


class PmPropertiesTab(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        sz = wx.BoxSizer(wx.VERTICAL)
        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_HORZ_TEXT)
        self.toolbar.AddTool(wx.ID_ADD, "Добавить свойство", get_icon("file-add"))
        self.toolbar.AddTool(wx.ID_DELETE, "Удалить свойство", get_icon("delete"))
        self.toolbar.EnableTool(wx.ID_ADD, False)
        self.toolbar.EnableTool(wx.ID_DELETE, False)
        self.toolbar.Realize()
        sz.Add(self.toolbar, 0, wx.EXPAND)
        self.propgrid = wx.propgrid.PropertyGrid(self)
        sz.Add(self.propgrid, 1, wx.EXPAND)
        self.SetSizer(sz)
        self.Layout()
        self.pm_sample: PMSample = None
        self.propgrid.Bind(wx.propgrid.EVT_PG_SELECTED, self.on_selection_changed)
        self.toolbar.Bind(wx.EVT_TOOL, self.on_add_property, id=wx.ID_ADD)
        self.toolbar.Bind(wx.EVT_TOOL, self.on_delete_property, id=wx.ID_DELETE)

    @db_session
    def on_add_property(self, event):
        dlg = PmPropertyDialog(self, self.pm_sample)
        if dlg.ShowModal() == wx.ID_OK:
            self.pm_sample = PMSample[self.pm_sample.RID]
            self.remove_properties()
            self.load_properties()
            self.update_controls_state()

    @db_session
    def on_delete_property(self, event):
        prop = self.propgrid.GetSelectedProperty()
        if prop is not None:
            if prop.GetName() == "Length1":
                PMSample[self.pm_sample.RID].Length1 = None
            elif prop.GetName() == "Length2":
                PMSample[self.pm_sample.RID].Length2 = None
            elif prop.GetName() == "Height":
                PMSample[self.pm_sample.RID].Height = None
            elif prop.GetName() == "MassAirDry":
                PMSample[self.pm_sample.RID].MassAirDry = None
            else:
                o = select(o for o in PmSamplePropertyValue if o.pm_property.Code == prop.GetName()).first()
                if o is not None:
                    o.delete()
                    commit()
        self.pm_sample = PMSample[self.pm_sample.RID]
        self.remove_properties()
        self.load_properties()
        self.update_controls_state()

    def on_selection_changed(self, event):
        self.update_controls_state()

    def set_pm_sample(self, pm_sample):
        self.pm_sample = pm_sample
        self.remove_properties()
        self.load_properties()
        self.update_controls_state()

    @db_session
    def load_properties(self):
        if self.pm_sample.Length1 is not None:
            self.propgrid.Append(wx.propgrid.FloatProperty("Сторона 1 (мм)", "Length1", self.pm_sample.Length1))
        if self.pm_sample.Length2 is not None:
            self.propgrid.Append(wx.propgrid.FloatProperty("Сторона 2 (мм)", "Length2", self.pm_sample.Length2))
        if self.pm_sample.Height is not None:
            self.propgrid.Append(wx.propgrid.FloatProperty("Высота (мм)", "Height", self.pm_sample.Height))
        if self.pm_sample.MassAirDry is not None:
            self.propgrid.Append(wx.propgrid.FloatProperty("Масса в воздушно сухом состоянии (г)", "MassAirDry", self.pm_sample.MassAirDry))
        for o in select(o for o in PmSamplePropertyValue if o.pm_sample == self.pm_sample):
            prop = o.pm_property
            self.propgrid.Append(wx.propgrid.FloatProperty("%s (%s)" % (prop.Name, prop.Unit), prop.Code, o.Value))
        self.propgrid.Update()

    def remove_properties(self):
        self.propgrid.Clear()
        self.propgrid.Update()

    def end(self):
        self.pm_sample = None
        self.remove_properties()
        self.update_controls_state()

    def update_controls_state(self):
        self.toolbar.EnableTool(wx.ID_ADD, self.pm_sample != None)
        self.toolbar.EnableTool(wx.ID_DELETE, self.pm_sample != None and self.propgrid.GetSelectedProperty() is not None)
