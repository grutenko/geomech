import wx
import wx.propgrid


class FastviewPmSampleSet(wx.propgrid.PropertyGrid):
    def __init__(self, parent):
        super().__init__(parent, style=wx.propgrid.PG_SPLITTER_AUTO_CENTER | wx.propgrid.PG_TOOLBAR)

        self.SetSplitterPosition(150)
        prop = self.Append(wx.propgrid.IntProperty("ID", "RID"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.StringProperty("№", "Number"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.LongStringProperty("Комментарий", "Comment"))
        self.SetPropertyReadOnly(prop)
        self.Hide()

    def start(self, o):
        self.Show()
