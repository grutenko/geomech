import config


class ClassConfigProvider:
    def __init__(self, class_name, version):
        self._class_name = class_name
        self._version = version
        if not config.has(class_name) or "@version" not in config.get(class_name) or config.get(class_name).__getitem__("@version") != version:
            self._config = {"@version": version}
        else:
            self._config = config.get(class_name)

    def __getitem__(self, key):
        return self._config[key] if key in self._config else None

    def __setitem__(self, key, value):
        self._config[key] = value

    def __delitem__(self, key):
        del self._config[key]

    def flush(self):
        config.set(self._class_name, self._config, flush_now=True)
