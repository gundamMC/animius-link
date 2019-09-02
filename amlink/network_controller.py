import json

from amlink import module_controller, SocketClient, socketio_server, SocketServer, config, utils


class Network:

    def __init__(self):
        cfg = config.get_config()
        self.id_username = {}  # Save request id and username
        self.ip = cfg['ip']
        self.socket_port = cfg['socket_port']
        self.socketio_port = cfg['socket.io_port']
        self.engine_port = cfg['engine_port']
        self.engine_passowrd = cfg['engine_password']

        self.serverThread, self.clients = SocketServer.start_server(self, self.socket_port, True)
        self.clientThread, self.clientSendQueue = SocketClient.start_client(self, self.ip, self.engine_port,
                                                                            self.engine_passowrd)
        self.socketio = socketio_server.SocketIOServer(self, self.socketio_port)

        self.local_commands = {'amlinkExit': utils.amlink_exit,
                               'amlinkCheckUpdate': utils.amlink_check_update,
                               'amlinkCheckInternet': utils.amlink_check_internet}

    def toEngine(self, id, cid, username, command, arguments, socketio):
        if command == 'waifuPredict':
            self.id_username[id] = [cid, username, True, socketio]
        else:
            self.id_username[id] = [cid, username, False, socketio]

        if command not in self.local_commands:
            self.clientSendQueue.put({'id': id, 'command': command, 'arguments': arguments})
        else:
            result = self.local_commands[command].__call__(id)
            self.toClient(SocketClient.Response.initFromResp(result))
            self.id_username.pop(id, None)

    def toClient(self, resp):
        id = resp.id
        status = resp.status
        message = resp.message
        data = resp.data
        cid = self.id_username[id][0]
        username = self.id_username[id][1]
        linkProcess = self.id_username[id][2]
        socketio = self.id_username[id][3]

        if message == 'success':

            if linkProcess and 'intent' in data.keys and 'ner' in data.keys:
                intent = data['intent']
                ner = SocketClient.parse_ner(data['ner'][0], data['ner'][1])
                return_value = module_controller.intents[intent].__call__(ner, username)
                return_value['intent'] = intent

            else:
                return_value = resp.data

            return_value = json.dumps(return_value)

            if socketio:
                self.socketio.sio.to(cid).emit(id, status, message, return_value)
            else:
                self.clients[cid].send(id, status, message, return_value)

            self.id_username.pop(id, None)
