import amlink

id_username = {}
ip = '127.0.0.1'
port = 44514

serverThread = amlink.SocketServer.start_server(port + 1, True)

clientThread = amlink.SocketClient.start_client(ip, port, '')


class NetworkHandler:

    @staticmethod
    def toEngine(id, cid, username, command, arguments):
        id_username[id] = [cid, username]
        clientThread.client.send(id, command, arguments)

    @staticmethod
    def toClient(resp):
        id = resp.id
        status = resp.status
        message = resp.message
        data = resp.data

        if message == 'success':
            intent = data['intent']
            ner = amlink.SocketClient.parse_ner(data['ner'])
            cid = id_username[id][0]
            username = id_username[id][1]
            return_value = amlink.module_controller.intents[intent].__call__(ner, username)
            serverThread.clients[cid].send(id, status, message, return_value)
