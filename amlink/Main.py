import json, queue

from amlink import SocketClient, SocketServer, module_controller

id_username = {}
ip = '127.0.0.1'
port = 23333

if __name__ == "__main__":
    # serverThread = SocketServer.start_server(port + 1, True)
    clientThread, sendQueue = SocketClient.start_client(ip, port, 'p@ssword')
    clientThread.client.send(0, 'getModels', '')
    sendQueue.put({'id': 0, 'command': 'getModels', 'arguments': ''})
    print('qq')
    sendQueue.put({'id': 0, 'command': 'gfffftModels', 'arguments': ''})


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

        if message == 'sucess':
            intent = data['intent']
            ner = SocketClient.parse_ner(data['ner'][0], data['ner'][1])
            cid = id_username[id][0]
            username = id_username[id][1]
            return_value = module_controller.intents[intent].__call__(ner, username)
            # return dict of data
            return_value = json.dumps(return_value).encode("utf-8")
            serverThread.clients[cid].send(id, status, message, return_value)
