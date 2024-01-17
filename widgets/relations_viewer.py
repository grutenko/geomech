import wx
import typing
import database
from .ui.relations_viewer import Ui_RelationsViewer

class RelationViewer(Ui_RelationsViewer):
    __relations: typing.List[typing.Tuple[str, database.Base]] = []

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.__relations = []
        self.tree.AppendColumn("Название")

    def set_relations(self, relations: typing.List[typing.Tuple[str, database.Base]]) -> None:
        self.__relations = relations
        for title, entities in self.__relations:
            item = self.tree.AppendItem(self.tree.GetRootItem(), title)
            for e in entities:
                part_item = self.tree.AppendItem(item, e.__str__())