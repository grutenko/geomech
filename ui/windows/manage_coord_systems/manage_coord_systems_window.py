import wx

from .tree import CoordSystemTree


class ManageCoordSystemsWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Системы координат",
            style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX | wx.FRAME_FLOAT_ON_PARENT,
        )
        self.SetIcon(wx.Icon("./icons/logo@16.jpg"))
        self.CenterOnParent()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self._tree = CoordSystemTree(self)
        main_sizer.Add(self._tree, 1, wx.EXPAND)

        self.Layout()
