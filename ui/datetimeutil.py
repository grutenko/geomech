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

def encode_datetime(date: wx.DateTime, hour, minute, seconds):
    return int(
        "%s%s%s%s%s%s"
        % (
            str(date.GetYear()),
            str(date.GetMonth() + 1).zfill(2),
            str(date.GetDay()).zfill(2),
            str(hour).zfill(2),
            str(minute).zfill(2),
            str(seconds).zfill(2),
        ))


def decode_date(n):
    return datetime.date(int(str(n)[:4]), int(str(n)[4:6]), int(str(n)[6:8]))


def decode_datetime(n):
    return datetime.datetime(
        int(str(n)[:4]),
        int(str(n)[4:6]),
        int(str(n)[6:8]),
        int(str(n)[8:10]),
        int(str(n)[10:12]),
        int(str(n)[12:14]),
    )
