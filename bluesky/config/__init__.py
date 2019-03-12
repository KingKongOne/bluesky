import copy

import afconfig

# make sure importing AVAILABLE_MODULES doesn't result in
# circular importsx
from bluesky import datetimeutils
from bluesky.exceptions import (
    BlueSkyDatetimeValueError
)
from bluesky.modules import AVAILABLE_MODULES
from .defaults import DEFAULTS

__all__ = [
    "Config",
    "DEFAULTS"
]

class Config:

    _RUN_ID = None
    _TODAY = None
    _RAW_CONFIG = copy.deepcopy(DEFAULTS)
    _CONFIG = copy.deepcopy(DEFAULTS)
    _IM_CONFIG = afconfig.ImmutableConfigDict(_CONFIG)

    def __new__(cls):
        # Never instantiate. Always return class object
        return cls

    @classmethod
    def reset(cls):
        cls._RUN_ID = None
        cls._TODAY = None
        cls._RAW_CONFIG = copy.deepcopy(DEFAULTS)
        cls._CONFIG = copy.deepcopy(DEFAULTS)
        cls._IM_CONFIG = afconfig.ImmutableConfigDict(cls._CONFIG)

        return cls

    @classmethod
    def merge(cls, config_dict):
        if config_dict:
            cls._RAW_CONFIG = afconfig.merge_configs(
                cls._RAW_CONFIG, copy.deepcopy(config_dict))
            cls._CONFIG = afconfig.merge_configs(cls._CONFIG,
                cls.replace_config_wildcards(copy.deepcopy(config_dict)))
            cls._IM_CONFIG = afconfig.ImmutableConfigDict(cls._CONFIG)

        return cls

    @classmethod
    def set(cls, config_dict, *keys):
        if keys:
            afconfig.set_config_value(cls._RAW_CONFIG,
                copy.deepcopy(config_dict), *keys)
            afconfig.set_config_value(cls._CONFIG,
                cls.replace_config_wildcards(copy.deepcopy(config_dict)),
                *keys)
            cls._IM_CONFIG = afconfig.ImmutableConfigDict(cls._CONFIG)

        else:
            cls._RAW_CONFIG = copy.deepcopy(DEFAULTS)
            cls._CONFIG = copy.deepcopy(DEFAULTS)
            cls.merge(config_dict)

        return cls

    @classmethod
    def set_today(cls, today):
        if today and cls._TODAY != today:
            cls._TODAY = today
            cls.set(cls._RAW_CONFIG)

    @classmethod
    def set_run_id(cls, run_id):
        if run_id and cls._RUN_ID != run_id:
            cls._RUN_ID = run_id
            cls.set(cls._RAW_CONFIG)

    @classmethod
    def get(cls, *keys, **kwargs):
        if 'default' in kwargs:
            raise DeprecationWarning("config defaults are specified in "
                "bluesky.config.defaults module")

        if keys:
            # default behavior is to fail if key isn't in user's config
            # or in default config
            return afconfig.get_config_value(cls._IM_CONFIG, *keys,
                fail_on_missing_key=not kwargs.get('allow_missing'))
        else:
            return cls._IM_CONFIG


    @classmethod
    def dump(cls, modules=None):
        if modules:
            # return all top level keys that are either
            #  not module-specific or which are in 'modules'
            return {k: cls._IM_CONFIG[k] for k in cls._IM_CONFIG
                if k not in AVAILABLE_MODULES or k in modules}
        else:
            return cls._IM_CONFIG

    @classmethod
    def replace_config_wildcards(cls, val):
        if isinstance(val, dict):
            for k in val:
                val[k] = cls.replace_config_wildcards(val[k])
        elif isinstance(val, list):
            val = [cls.replace_config_wildcards(v) for v in val]
        elif hasattr(val, 'lower'):  # i.e. it's a string
            if val:
                # first, fill in any datetime control codes or wildcards
                val = datetimeutils.fill_in_datetime_strings(val,
                    today=cls._TODAY)

                # then, see if the resulting string purely represents a datetime
                try:
                    val = datetimeutils.to_datetime(val, limit_range=True)
                except BlueSkyDatetimeValueError:
                    pass

                if hasattr(val, 'capitalize'):
                    # This gets rid of datetime parsing busters embedded
                    # in strings to prevent conversion to datetime object
                    val = val.replace('{datetime-parse-buster}', '')

                    if cls._RUN_ID:
                        val = val.replace('{run_id}', cls._RUN_ID)

                # TODO: any other replacements?

        return val
