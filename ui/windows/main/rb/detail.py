import wx


class RockBurstDetail(wx.Panel):
    def __init__(self, parent, rock_burst):
        super().__init__(parent)
        self.rock_burst = rock_burst
