import importlib


def import_from_string(val):
    module_path, class_name = val.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)
