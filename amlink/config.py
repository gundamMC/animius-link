import json

config = {
  'allow_registration':  True,
  'register_key': 'some random key',
  'ip': '127.0.0.1',
  'socket_port': 5001,
  'socket.io_port': 5000
}


def load(path='./config.json'):

    global config

    try:
        with open(path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print('config file not found, resorting to default configs')
        try:
            with open(path, 'w') as f:
                json.dump(config, f, indent=4)
        except IOError as e:
            print('Error while creating new config file')
            print(e)


if config is None:
    load()
