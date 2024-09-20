import config

__version__ = 6
__key__ = "main_window"


class ConfigProvider:
    def __init__(self):
        if (
            not config.has(__key__)
            or "@version" not in config.get(__key__)
            or config.get(__key__).__getitem__("@version") != __version__
        ):
            self._config = {
                "@version": __version__
            }
        else:
            self._config = config.get(__key__)

    def get_perspective(self):
        if 'perspective' not in self._config:
            return None
        return self._config['perspective']
    
    def set_perspective(self, perspective):
        self._config['perspective'] = perspective

    def get_window_options(self):
        if not 'options' in self._config:
            return None
        return self._config['options']
    
    def set_window_options(self, options):
        self._config['options'] = options

    def toggle_fastview(self, showed):
        self._config['toggle_fastview'] = showed

    def toggle_supplied_data(self, showed):
        self._config['toggle_supplied_data'] = showed

    def get_toggle_fastview(self):
        if "toggle_fastview" not in self._config:
            return True
        return self._config['toggle_fastview']
    
    def get_toggle_supplied_data(self):
        if "toggle_supplied_data" not in self._config:
            return True
        return self._config['toggle_supplied_data']

    def flush(self):
        config.set(__key__, self._config, flush_now=True)
