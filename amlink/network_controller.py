from amlink import socket_server, config, utils


class Network:

    def __init__(self):
        cfg = config.get_config()
        self.ip = cfg['ip']
        self.socket_port = cfg['socket_port']
        self.socketio_port = cfg['socket.io_port']
        self.engine_port = cfg['engine_port']
        self.engine_passowrd = cfg['engine_password']

        self.socket_server = socket_server.SocketServer(self.socket_port, True, self.engine_passowrd, 10, self.ip,
                                                        self.engine_port)
        # self.socketio = socketio_server.SocketIOServer(self, self.socketio_port)

        self.local_commands = {'amlinkExit': utils.amlink_exit,
                               'amlinkCheckUpdate': utils.amlink_check_update,
                               'amlinkCheckInternet': utils.amlink_check_internet}
