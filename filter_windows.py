import wx
from database import get_session
from ui import Ui_DischargeMeasurement_Filter
import mixins
import query_dsl

class DischargeMeasurement_Filter(Ui_DischargeMeasurement_Filter, mixins.OptionalFieldsMixin):
    __filter_by: query_dsl.FilterBy

    def __init__(self, filter_by: query_dsl.FilterBy = query_dsl.FilterBy(), *args, **kwds):
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)
        self.__filter_by = filter_by

        self.__set_fields()

    def __set_fields(self):
        pass