import wx
import wx.lib.wxcairo


class GridSamplesPreview(wx.Frame):
    def __init__(self, parent, pm_sample_set):
        super().__init__(
            parent,
            title="Предпросмотр: Проба %s" % pm_sample_set.Number,
            style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW | wx.CLIP_CHILDREN | wx.STAY_ON_TOP | wx.NO_BORDER | wx.FRAME_SHAPED,
            size=wx.Size(200, 400),
        )
        sz = wx.BoxSizer(wx.VERTICAL)
        self.panel = wx.Panel(self)
        sz.Add(self.panel, 1, wx.EXPAND)
        self.dc = wx.WindowDC(self)
        wx.lib.wxcairo.ContextFromDC(self.dc)
        self.SetSizer(sz)
        self.Layout()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        self.Hide()
