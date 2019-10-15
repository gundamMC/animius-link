# import json
# import queue
# import socket
# import struct
# import threading
#
#
# class Request:
#
#     @staticmethoda
#     def createReq(id, command, arguments):
#         req = {"id": id,
#                "command": command,
#                "arguments": arguments
#                }
#         return json.dumps(req)
#
#
# class Response:
#
#     def __init__(self, id, status, message, data):
#         self.id = id
#         self.status = status
#         self.message = message
#         self.data = data
#
#     @classmethod
#     def initFromResp(cls, resp):
#         respJson = json.loads(resp)
#         return cls(respJson["id"], respJson["status"], respJson["message"], respJson['data'])
#
#
# class Client:
#     def __init__(self, ip, port):
#         self.ip = ip
#         self.port = port
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
#     def connect(self, pwd):
#         self.socket.connect((self.ip, self.port))
#         self.send('', 'login', {'pwd': pwd})
#
#     def send(self, id, command, arguments):
#         req = Request.createReq(id, command, arguments)
#         print(req)
#         self._send(req)
#
#     def _send(self, data):
#         print('socket_send', data)
#         data = data.encode('utf-8')
#         length = len(data)
#         self.socket.sendall(struct.pack('!I', length))
#         self.socket.sendall(data)
#
#     def _recvall(self, count):
#         buf = b''
#         while count:
#             newbuf = self.socket.recv(count)
#             if not newbuf:
#                 return None
#             buf += newbuf
#             count -= len(newbuf)
#         return buf
#
#     def _recv(self):
#         lengthbuf = self._recvall(4)
#         length, = struct.unpack('!I', lengthbuf)
#         return self._recvall(length)
#
#     def recv(self):
#         resp = self._recv()
#         resp = resp.decode()
#         resp = Response.initFromResp(resp)
#
#         if resp.id == '':
#             return None
#         else:
#             return resp
#
#     def close(self):
#         self.send('', 'logout', {})
#         self.socket.close()
#
#
# def create_client_thread(network, ip, port, pwd, sendQueue):
#     client = Client(ip, port)
#     queue = sendQueue
#     sendThread = threading.Thread(target=send_queue, args=(client, queue))
#     sendThread.daemon = True
#     client.connect(pwd)
#
#     sendThread.start()
#
#     while True:
#         resp = client.recv()
#
#         if resp is None or resp is "":
#             continue
#         network.toClient(resp)
#
#
# def send_queue(client, queue):
#     while True:
#         if not queue.empty():
#             result = queue.get()
#             client.send(result['id'], result['command'], result['arguments'])
#             queue.task_done()
#
#
# def start_client(network, ip, port, pwd):
#     sendQueue = queue.Queue(0)
#     thread = threading.Thread(target=create_client_thread, args=(network, ip, port, pwd, sendQueue))
#     thread.daemon = True
#     thread.start()
#     return thread, sendQueue
#
#
# def parse_ner(sentence, ner):
#     # sentence and ner should be two lists of strings
#     # e.g.
#     # sentence = ['weather', 'in', 'san', 'francisco', 'tonight', 'at', '6', 'pm', '?']
#     # ner = ['', '', 'place', 'place', 'time', '', 'time', 'time', '']
#
#     output = {}  # dict of list
#     last_label = ''
#
#     for i in range(len(sentence)):
#         word = sentence[i]
#         label = ner[i]
#
#         if label != '':
#             if label == last_label:  # consecutive words
#                 output[label][-1] = output[label][-1] + ' ' + word
#             else:
#                 if label in output:  # already existing label
#                     output[label].append(word)
#                 else:  # new label
#                     output[label] = [word]
#
#         last_label = label
#
#     return output
