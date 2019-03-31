import amlink

ip = '127.0.0.1'
port = 44514
pwd = ''

serverThread = amlink.SocketServer.start_server(port + 1, True, '')

clientThread = amlink.SocketClient.start_client(ip, port, pwd)


class NetworkHandler:
    @staticmethod
    def toEngine(id, command, arguments):
        clientThread.client.send(id, command, arguments)

    @staticmethod
    def toClient(id, status, message, data):
        serverThread.client.send(id, status, message, data)
