import wx
import datetime


def encode_date(date: wx.DateTime):
    return int(
        "%s%s%s000000"
        % (
            str(date.GetYear()),
            str(date.GetMonth() + 1).zfill(2),
            str(date.GetDay()).zfill(2),
        )
    )


def decode_date(n):
    return datetime.date(int(str(n)[:4]), int(str(n)[4:6]), int(str(n)[6:8]))
