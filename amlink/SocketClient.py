import json
import socket
import threading
import queue
import amlink


class Request:

    @staticmethod
    def createReq(id, command, arguments):
        req = {"id": id,
               "command": command,
               "arguments": arguments
               }
        return json.dumps(req)


class Response:

    def __init__(self, id, status, message, data):
        self.id = id
        self.status = status
        self.message = message
        self.data = data

    @classmethod
    def initFromResp(cls, resp):
        respJson = json.loads(resp)
        return cls(respJson["id"], respJson["status"], respJson["message"], respJson['data'])


class Client:
    def __init__(self, ip, port):
        if ip:
            self.ip = ip
        else:
            self.ip = 'localhost'

        if port:
            self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, pwd):
        self.socket.connect((self.ip, self.port))
        self._send(pwd)

    def send(self, id, command, arguments):
        req = Request.createReq(id, command, arguments)
        print(req)
        self._send(req)

    def _send(self, msg):
        self.socket.send(msg.encode('utf-8'))

    def recv(self):
        try:
            resp = self._recv()
            resp = resp.decode()
            print(resp)
            resp = Response.initFromResp(resp)
            return resp

        finally:
            return None

    def _recv(self, mtu=65535):
        return self.socket.recv(mtu)

    def close(self):
        self.socket.close()


class ClientThread(threading.Thread):
    def __init__(self, ip, port, pwd, sendQueue):
        threading.Thread.__init__(self)
        self.pwd = pwd
        self.client = Client(ip, port)
        self.queue = sendQueue

    def run(self):
        self.client.connect(self.pwd)

        while True:
            # if not self.queue.empty():
            #     result = self.queue.get()
            #     self.client.send(result['id'], result['command'], result['arguments'])
            #     self.queue.task_done()

            resp = self.client.recv()
            if resp is None or resp is "":
                continue
            amlink.NetworkHandler.toClient(resp)

    def stop(self):
        self.client.close()


def start_client(ip, port, pwd):
    sendQueue = queue.Queue(0)
    thread = ClientThread(ip, port, pwd, sendQueue)
    thread.run()
    return thread, sendQueue


def parse_ner(sentence, ner):
    # sentence and ner should be two lists of strings
    # e.g.
    # sentence = ['weather', 'in', 'san', 'francisco', 'tonight', 'at', '6', 'pm', '?']
    # ner = ['', '', 'place', 'place', 'time', '', 'time', 'time', '']

    output = {}  # dict of list
    last_label = ''

    for i in range(len(sentence)):
        word = sentence[i]
        label = ner[i]

        if label != '':
            if label == last_label:  # consecutive words
                output[label][-1] = output[label][-1] + ' ' + word
            else:
                if label in output:  # already existing label
                    output[label].append(word)
                else:  # new label
                    output[label] = [word]

        last_label = label

    return output
