from django.conf import settings

from .utils import import_from_string

DEFAULT_SETTINGS = {
    'async': False,
    'handlers': [],
    'default_lang': 'en',
}

IMPORT_STRINGS = [
    'handlers'
]

EXTRA_SETTINGS = {
    'skip_send': False
}


class MsgSettings:
    _cache = {}

    def __init__(self, default, user_config, import_strings, extra):
        self.default = default
        self.user_config = user_config
        self.import_strings = import_strings
        self.extra = extra

    def __getattr__(self, item):
        if not (item in self.default or item in self.extra):
            raise ValueError(f'MsgSettings has no attribute {item!r}.')

        if item in self.import_strings:
            if item in self._cache:
                return self._cache[item]

            val = self.import_setting(item)
            return val

        if item in self.user_config:
            return self.user_config[item]

        if item in self.extra:
            return self.get_extra(item)

        return self.default[item]

    def import_setting(self, item):
        val = [
            import_from_string(s) for s
            in self.user_config[item]
        ]
        self._cache[item] = val
        return val

    def get_extra(self, item: 'str'):
        key = f'MSG_{item.upper()}'
        return getattr(settings, key, self.extra[item])


msg_settings = MsgSettings(
    DEFAULT_SETTINGS,
    getattr(settings, 'MSG_SETTINGS', {}),
    IMPORT_STRINGS,
    EXTRA_SETTINGS,
)
