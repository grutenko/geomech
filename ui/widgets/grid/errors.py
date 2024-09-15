import wx

from wx.lib.agw.flatnotebook import FlatNotebookCompatible

class Errors(wx.Panel):
    def __init__(self, parent, error_image = None):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.notebook = FlatNotebookCompatible(self, agwStyle=0)
        main_sizer.Add(self.notebook, 1, wx.EXPAND)

        self._image_list = wx.ImageList(16, 16)
        if error_image != None:
            self._error_image = self._image_list.Add(error_image)
        else:
            self._error_image = -1
        
        error_panel = wx.Panel(self.notebook)
        error_sizer = wx.BoxSizer(wx.VERTICAL)
        self.list = wx.ListCtrl(error_panel, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)
        self.list.AppendColumn("Столбец", width=120)
        self.list.AppendColumn("Строка", width=60)
        self.list.AppendColumn("Ошибка", width=450)
        error_sizer.Add(self.list, 1, wx.EXPAND)

        error_panel.SetSizer(error_sizer)
        self.notebook.AddPage(error_panel, "Ошибки", imageId=self._error_image)

        self.SetSizer(main_sizer)