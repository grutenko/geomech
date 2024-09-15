import wx


class CreateTransfMatrixWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Утилита нахождения матрицы перехода",
            style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX | wx.FRAME_FLOAT_ON_PARENT,
        )
        self.SetIcon(wx.Icon("./icons/logo@16.jpg"))
        self.CenterOnParent()
