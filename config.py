import wx
import json
import attrdict2
import os.path
from options import __PROGRAM_HOME__
from typing import Dict, Optional

_config_filename = os.path.join(__PROGRAM_HOME__, "config.json")
_config: Dict[str, attrdict2.AttrDict] = {}
_fallback_runtime_config: bool = False


def configure():
    global _config, _fallback_runtime_config, _config_filename
    try:
        if not os.path.isfile(_config_filename):
            if not os.path.isdir(__PROGRAM_HOME__):
                os.mkdir(__PROGRAM_HOME__)
            with open(_config_filename, "a") as f:
                f.write("{}")
        with open(_config_filename) as f:
            _data = json.load(f)
            if isinstance(_data, dict):
                for key, sect in _data.items():
                    _config[key] = attrdict2.AttrDict(sect)
    except (OSError, json.JSONDecodeError) as e:
        _fallback_runtime_config = True
        wx.MessageBox(
            "Не удалось открыть файл конфигурации: %s. %s" % (_config_filename, str(e)),
            "Ошибка",
            style=wx.OK | wx.CENTRE | wx.ICON_ERROR,
        )


def get(key: str) -> Optional[attrdict2.AttrDict]:
    global _config
    if key not in _config:
        return None
    return _config[key]


def set(key: str, value: attrdict2.AttrDict, flush_now=False):
    global _config
    _config[key] = value
    if flush_now:
        flush()


def has(key: str) -> bool:
    global _config
    return key in _config


import shutil


def flush():
    global _config, _config_filename, _fallback_runtime_config
    if _fallback_runtime_config:
        return
    _tmp_filename = _config_filename + ".tmp"
    f = open(_tmp_filename, "w")
    try:
        f.write(json.dumps(_config, indent=4))
        f.close()
    except Exception:
        raise
    else:
        shutil.copyfile(_tmp_filename, _config_filename)
    finally:
        os.remove(_tmp_filename)