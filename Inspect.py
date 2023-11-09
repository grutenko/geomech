from typing import Type
import database
from Ui_Inspect import Ui_Inspect

class Inspect(object):
    def __init__(self, parent, model: Type[database.Base]) -> None:
        self.ui = Ui_Inspect(parent)

    def Show(self):
        self.ui.Show()