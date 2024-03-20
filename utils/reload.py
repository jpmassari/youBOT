import importlib
import sys

def reload_module(module_name):
    importlib.reload(sys.modules[module_name])
    return importlib.import_module(module_name)