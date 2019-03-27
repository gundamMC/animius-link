import json
import socket
import threading

clients = {}


class Request:
    def __init__(self, id, command, arguments):
        self.id = id
        self.command = command
        self.arguments = arguments

    @classmethod
    def initFromReq(cls, req):
        try:
            data = json.loads(req)
            return cls(data["id"], data["command"], data["arguments"])
        except:
            return None


class Response:

    @staticmethod
    def createResp(response_id, status, message, data):
        resp = {"id": response_id,
                "status": status,
                "message": message,
                "data": data
                }
        return json.dumps(resp).encode("utf-8")


class Client:
    def __init__(self, socket, address, pwd):
        self.address = address[0]
        self.port = address[1]
        self.pwd = pwd
        self.socket = socket

    def _send(self, data):
        self.socket.send(data)

    def _recv(self, mtu=65535):
        return self.socket.recv(mtu)

    def send(self, id, status, message, data):
        resp = Response.createResp(id, status, message, data)
        self._send(resp)

    def recv(self):
        try:
            req = self._recv()
            req = req.decode()
            req = Request.initFromReq(req)
            return req
        except:
            return None

    def recv_pass(self):
        req = self._recv()
        req = req.decode()

        return req

    def close(self):
        self.socket.close()


def new_client(c, event):
    # check if event is set (then this client is probably the 'fake' one from stop())
    if event.is_set():
        return

    try:
        print('Establishing connection with: {0}:{1}'.format(c.address, c.port))
        # check for password
        if c.pwd != '':
            recvPwd = c.recv_pass()
            if recvPwd != c.pwd:
                # wrong password, close connection
                c.close()

        # password verified and connected
        c.send('', 0, 'success', {})

        while True:
            req = c.recv()
            response = handle_network(req)
            c.send(response)

    except socket.error as error:
        print('Socket error from {0}: {1]'.format(c.address, error))
    except Exception as error:
        print('Unexpected exception from {0}: {1}'.format(c.address, error))
    finally:
        print('Closing connection with {0}:{1}'.format(c.address, c.port))
        c.close()


def start_server(port, local=True, pwd='', max_clients=10):
    thread = _ServerThread(port, local, pwd, max_clients)
    thread.start()
    return thread


class _ServerThread(threading.Thread):
    def __init__(self, port, local=True, pwd='', max_clients=10):
        super(_ServerThread, self).__init__()
        self.event = threading.Event()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.port = port

        if local:
            self.host = '127.0.0.1'
        else:
            self.host = socket.gethostname()
        self.server.bind((self.host, port))

        self.pwd = pwd
        self.max_clients = max_clients

    def run(self):
        # Start Listening
        self.server.listen(self.max_clients)

        while not self.event.is_set():
            # Accept Connection
            conn, addr = self.server.accept()
            c = Client(conn, addr, self.pwd)
            t = threading.Thread(target=new_client, args=(c, self.event))
            t.start()

        # close server
        self.server.close()
        print('Server closed')

    def stop(self):
        self.event.set()
        # let the while loop in run() know to stop

        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.host, self.port))
        # send a fake client to let run() move on from self.server.accept()


def handle_network(req):
    id = req.id
    command = req.command
    arguments = req.arguments

    return req
