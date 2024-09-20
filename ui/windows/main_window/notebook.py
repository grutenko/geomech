import wx
from wx.lib.newevent import NewEvent
from wx.lib.agw.flatnotebook import *

NotebookTitleChanged, EVT_NOTEBOOK_TITLE_CHANGED = NewEvent()

class NotebookPage(wx.Panel):
    def on_close(self) -> bool: ...
    def on_select(self): ...
    def on_deselect(self): ...
    def get_title(self) -> str:
        return "Вкладка"
    def set_title(self, title): ...

class MainWindowNotebook(wx.Panel):
    _instance = None
    
    @classmethod
    def get_instance(cls):
        return cls._instance

    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.notebook = FlatNotebook(self, agwStyle=FNB_X_ON_TAB)
        self.notebook.Bind(EVT_FLATNOTEBOOK_PAGE_CHANGED, self._on_page_changed)
        self.notebook.Bind(EVT_FLATNOTEBOOK_PAGE_CLOSING, self._on_page_closing)
        self.notebook.Bind(EVT_NOTEBOOK_TITLE_CHANGED, self._on_title_changed)
        self._native_ = self.notebook
        main_sizer.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        self.Layout()

        self.__class__._instance = self

    def add_page(self, page):
        self.notebook.AddPage(page, page.get_title(), False)
        self.notebook.SetSelection(self.notebook.GetPageCount() - 1)

    def _on_page_changed(self, event: FlatNotebookEvent):
        new_index = event.GetSelection()
        old_index = event.GetOldSelection()
        if old_index != -1 and old_index != new_index:
            page = self.notebook.GetPage(old_index)
            if page != None:
                page.on_deselect()
        if new_index != -1:
            page = self.notebook.GetPage(new_index)
            if page != None:
                page.on_select()

    def _on_page_closing(self, event):
        index = event.GetSelection()
        if index != -1:
            page = self.notebook.GetPage(index)
            if not page.on_close():
                event.Veto()

    def _on_title_changed(self, event):
        index = self.notebook.GetPageIndex(event.target)
        if index != -1:
            self.notebook.SetPageText(index, event.target.get_title())