import importlib
import os


intents = {}
modules = {}


def load():
    for file in os.listdir('modules'):
        if file.endswith('Module.py'):
            name = file.replace('.py', '')
            modules[name] = importlib.import_module('amlink.modules.' + name)

            if hasattr(modules[name], 'register_intents'):
                intents.update(modules[name].register_intents)


load()

print('intents' + str(intents))

intents['weather'].__call__('some ner data', 'gundamMC')