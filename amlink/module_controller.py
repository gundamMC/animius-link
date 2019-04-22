import importlib
import os

intents = {}
modules = {}
start = []
end = []


def load():
    for file in os.listdir('modules'):
        if file.endswith('Module.py'):
            name = file.replace('.py', '')
            modules[name] = importlib.import_module('amlink.modules.' + name)

            if hasattr(modules[name], 'register_intents'):
                intents.update(modules[name].register_intents)

            if hasattr(modules[name], 'start'):
                start.append(modules[name].start)

            if hasattr(modules[name], 'end'):
                end.append(modules[name].end)

    for func in start:
        func()


def unload():
    global intents, modules, start, end
    for func in end:
        func()
    intents = {}
    modules = {}
    start = []
    end = []


load()

print('intents' + str(intents))

# intents['weather'].__call__('some ner data', 'gundamMC')
