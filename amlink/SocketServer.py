import json
import socket
import struct
import threading


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
        return json.dumps(resp)


class Client:
    def __init__(self, socket, address, cid):
        self.address = address[0]
        self.port = address[1]
        self.socket = socket
        self.cid = cid

    def _send(self, data):
        data = data.encode('utf-8')
        length = len(data)
        self.socket.sendall(struct.pack('!I', length))
        self.socket.sendall(data)

    def _recvall(self, count):
        buf = b''
        while count:
            newbuf = self.socket.recv(count)
            if not newbuf:
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def _recv(self):
        lengthbuf = self._recvall(4)
        length, = struct.unpack('!I', lengthbuf)
        return self._recvall(length)

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


def new_client(network, client, event):
    # check if event is set (then this client is probably the 'fake' one from stop())
    if event.is_set():
        return

    print('Establishing connection with: {0}:{1}'.format(client.address, client.port))

    # "Username,Password"
    recv = client.recv_pass()
    recv = recv.split(',')
    user_name = recv[0]
    password = recv[1]

    # user_object = amlink.users.get_user(user_name)
    #
    # if user_object.checkPassword(password) is False:
    #     # wrong password, close connection
    #     c.close()
    print(user_name, password)
    client.send('', 0, 'Login: {0}'.format(user_name), {})

    while True:
        req = client.recv()
        handle_network(network, req, client.cid, user_name)  # user_object.name)

    # except socket.error as error:
    #     print('Socket error from {0}: {1]'.format(c.address, error))
    # except Exception as error:
    #     print('Unexpected exception from {0}: {1}'.format(c.address, error))
    # finally:
    #     print('Closing connection with {0}:{1}'.format(c.address, c.port))
    #     c.close()


def start_server(network, port, local=True, max_clients=10):
    thread = threading.Thread(target=create_server_thread, args=(network, port, local, max_clients))
    thread.daemon = True
    thread.start()
    return thread


def create_server_thread(network, port, local=True, max_clients=10):
    event = threading.Event()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    clients = list()

    if local:
        host = '127.0.0.1'
    else:
        host = socket.gethostname()
    server.bind((host, port))
    max_clients = max_clients

    # Start Listening
    server.listen(max_clients)

    while not event.is_set():
        # Accept Connection
        conn, addr = server.accept()

        cid = len(clients)
        clients.append(Client(conn, addr, cid))

        t = threading.Thread(target=new_client, args=(network, clients[cid], event))
        t.start()

    # close server
    server.close()
    print('Server closed')


def handle_network(network, req, cid, username):
    id = req.id
    command = req.command
    arguments = req.arguments
    username = username

    network.toEngine(id, cid, username, command, arguments)
