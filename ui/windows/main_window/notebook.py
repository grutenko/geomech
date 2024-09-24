import wx
from wx.lib.newevent import NewEvent
from wx.lib.agw.flatnotebook import *
from dataclasses import dataclass
from typing import Tuple, Optional

NotebookTitleChanged, EVT_NOTEBOOK_TITLE_CHANGED = NewEvent()
NotebookPageCountChanged, EVT_NOTEBOOK_PAGE_COUNT_CHANGED = NewEvent()
NotebookPageSelectionChanged, EVT_NOTEBOOK_PAGE_SELECTION_CHANGED = NewEvent()


@dataclass
class NotebookPageIdentity:
    object: any
    property: Tuple[any, any]

    def __eq__(self, identity):
        return (
            isinstance(identity, NotebookPageIdentity)
            and identity.object == self.object
            and identity.property[0] == self.property[0]
            and identity.property[1] == self.property[1]
        )


class NotebookPage(wx.Panel):
    def get_identity(self) -> Optional[NotebookPageIdentity]: ...
    def on_close(self) -> bool: ...
    def on_select(self): ...
    def on_deselect(self): ...
    def get_title(self) -> str:
        return "Вкладка"

    def get_font_color(self) -> wx.Font: ...
    def get_head_color(self) -> wx.Colour: ...


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
        self.notebook.Bind(EVT_FLATNOTEBOOK_PAGE_CLOSED, self._on_page_closed)
        self._native_ = self.notebook
        main_sizer.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        self.Layout()

        self.__class__._instance = self

        self._close_page_accepted = False

    def select_by_identity(self, identity) -> bool:
        for index in range(self.notebook.GetPageCount()):
            page = self.notebook.GetPage(index)
            if page.get_identity() != None and page.get_identity().__eq__(identity):
                old_selection = self.notebook.GetSelection()
                self.notebook.SetSelection(index)
                self._page_changed(index, old_selection)
                return True
        return False

    def add_page(self, page):
        title = page.get_title()
        self.notebook.AddPage(
            page, (title if len(title) < 30 else title[:30] + "..."), True
        )
        index = self.notebook.GetPageCount() - 1
        self.notebook.SetPageTextColour(index, page.get_font_color())
        page.Bind(EVT_NOTEBOOK_TITLE_CHANGED, self._on_title_changed)
        wx.PostEvent(
            self,
            NotebookPageCountChanged(target=self, count=self.notebook.GetPageCount()),
        )

    def close_current_page(self):
        self.notebook.DeletePage(self.notebook.GetSelection())

    def _on_page_changed(self, event: FlatNotebookEvent):
        new_index = event.GetSelection()
        old_index = event.GetOldSelection()
        self._page_changed(new_index, old_index)

    def _page_changed(self, new_index, old_index):
        if old_index != -1 and old_index != new_index:
            page = self.notebook.GetPage(old_index)
            if page != None:
                page.on_deselect()
        if new_index != -1:
            page = self.notebook.GetPage(new_index)
            if page != None:
                page.on_select()
        wx.PostEvent(
            self,
            NotebookPageSelectionChanged(
                target=self, old_index=old_index, new_index=new_index
            ),
        )

    def _on_page_closed(self, event):
        wx.PostEvent(
            self,
            NotebookPageCountChanged(target=self, count=self.notebook.GetPageCount()),
        )

    def _on_page_closing(self, event):
        index = event.GetSelection()
        if not self._page_closing(index):
            event.Veto()
            self._close_page_accepted = False
        else:
            self._close_page_accepted = True

    def _page_closing(self, index):
        if index != -1:
            page = self.notebook.GetPage(index)
            if not page.on_close():
                return False
            else:
                page.Unbind(EVT_NOTEBOOK_TITLE_CHANGED, handler=self._on_title_changed)
        return True

    def _on_title_changed(self, event):
        index = self.notebook.GetPageIndex(event.target)
        if index != -1:
            self.notebook.SetPageText(index, event.target.get_title())
            self.notebook.SetPageTextColour(index, event.target.get_font_color())

    def can_go_next(self):
        return self.notebook.GetSelection() < self.notebook.GetPageCount() - 1

    def can_go_prev(self):
        return self.notebook.GetSelection() > 0

    def go_next(self):
        index = self.notebook.GetSelection()
        if index < self.notebook.GetPageCount() - 1:
            self.notebook.SetSelection(index + 1)
            self._page_changed(index + 1, index)

    def go_prev(self):
        index = self.notebook.GetSelection()
        if index > 0:
            self.notebook.SetSelection(index - 1)
            self._page_changed(index - 1, index)

    def get_page_count(self):
        return self.notebook.GetPageCount()
    
    def close_all(self):
        for index in range(self.get_page_count()):
            self.notebook.DeletePage(index)
            if not self._close_page_accepted:
                return False
            
        return True
