import functools
from types import SimpleNamespace
from copy import deepcopy
import json


# https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-subobjects-chained-properties
def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition(".")
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split("."))


class Config:
    class ConfigContext:
        def __init__(self, config, d):
            self._original_namespace = deepcopy(config.namespace)
            self.config = config
            for k, v in d.items():
                rsetattr(self.config.namespace, k, v)

        def __enter__(self):
            return self.config

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.config.namespace = self._original_namespace

    def __init__(self, json_string):
        self.namespace = json.loads(
            json_string, object_hook=lambda d: SimpleNamespace(**d)
        )

    def __getattr__(self, item):
        return getattr(self.namespace, item)

    def __call__(self, override_dict):
        return self.ConfigContext(self, override_dict)
