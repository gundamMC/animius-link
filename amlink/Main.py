import amlink

ip = '127.0.0.1'
port = 44514

serverThread = amlink.SocketServer.start_server(port + 1, True)

clientThread = amlink.SocketClient.start_client(ip, port, '')


class NetworkHandler:
    @staticmethod
    def toEngine(id, uid, command, arguments):
        clientThread.client.send(id, uid, command, arguments)

    @staticmethod
    def toClient(id, status, message, data):
        serverThread.client.send(id, status, message, data)
