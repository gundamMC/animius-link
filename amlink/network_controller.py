import json

from amlink import module_controller, SocketClient, SocketServer


class Network:

    def __init__(self):
        self.id_username = {}  # Save request id and username
        self.ip = '127.0.0.1'  # config['ip']
        self.socket_port = 5001  # config['socket_port']
        self.engine_port = 5002  # config['engine_port']
        self.engine_passowrd = 'p@ssword'  # config['engine_password']
        self.serverThread = SocketServer.start_server(self, self.socket_port, True)
        self.clientThread, self.clientSendQueue = SocketClient.start_client(self, self.ip, self.engine_port,
                                                                            self.engine_passowrd)

    def toEngine(self, id, cid, username, command, arguments):
        if command == 'waifuPredict':
            self.id_username[id] = [cid, username, True]
        else:
            self.id_username[id] = [cid, username, False]

        self.clientSendQueue.put({'id': id, 'command': command, 'arguments': arguments})

    def toClient(self, resp):
        print('toClient')
        id = resp.id
        status = resp.status
        message = resp.message
        data = resp.data
        cid = self.id_username[id][0]
        username = self.id_username[id][1]
        linkProcess = self.id_username[id][2]

        if message == 'success':
            if linkProcess and 'intent' in data.keys and 'ner' in data.keys:
                intent = data['intent']
                ner = SocketClient.parse_ner(data['ner'][0], data['ner'][1])
                return_value = module_controller.intents[intent].__call__(ner, username)
                return_value['intent'] = intent

            else:
                return_value = resp.data

            return_value = json.dumps(return_value).encode("utf-8")
            self.serverThread.clients[cid].send(id, status, message, return_value)