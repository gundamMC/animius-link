import asyncio
import json

from amlink import module_controller, network_controller


class Connect:
    def __init__(self, engine_ip, engine_port, pwd, server, socketio):
        self.engine_ip = engine_ip
        self.engine_port = engine_port
        self.pwd = pwd
        self.reader = self.writer = None
        self.server = server
        self.socketio = socketio

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.engine_ip, self.engine_port)
        valid_session, auth_message = await self.send_auth(self.writer)

        while valid_session:
            raw_response = await network_controller.NetworkProtocol.await_receive(self.reader)
            response_id, message, status, data = network_controller.NetworkProtocol.parse_response(raw_response)

            if response_id in self.server.pending_requests:
                link_process = self.server.pending_requests[response_id][1]
                username = self.server.pending_requests[response_id][2]

                if data != {} and link_process and 'intent' in data.keys and 'ner' in data.keys:
                    intent = data['intent']
                    ner = self.parse_ner(data['ner'][0], data['ner'][1])
                    return_value = module_controller.intents[intent].__call__(ner, username)
                    return_value['intent'] = intent
                else:
                    return_value = data

                if self.socketio:
                    sid = self.server.pending_requests[response_id][0]
                    self.server.sio.to(sid).emit(response_id, status, message, return_value)
                else:
                    response = network_controller.NetworkProtocol.create_response(response_id, message, status,
                                                                                  json.dumps(return_value))
                    await network_controller.NetworkProtocol.await_write(self.server.pending_requests[response_id][0],
                                                                         response)

                self.server.pending_requests.pop(response_id, None)

    async def send_auth(self, writer):
        auth = network_controller.NetworkProtocol.create_request(None, "login", {"pwd": self.pwd})
        await network_controller.NetworkProtocol.await_write(writer, auth)
        return True, "success"

    async def send_request(self, request_id, command, arguments):
        request = network_controller.NetworkProtocol.create_request(request_id, command, arguments)
        await network_controller.NetworkProtocol.await_write(self.writer, request)

    @staticmethod
    def parse_ner(sentence, ner):
        # sentence and ner should be two lists of strings
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
