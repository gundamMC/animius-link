import asyncio
import json
import struct
import time


class ConnectLink:
    @staticmethod
    async def await_write(writer, data):
        writer.write(struct.pack('!I', len(data)))
        writer.write(data)
        await writer.drain()

    @staticmethod
    async def await_receive(reader):
        length_buf = await reader.read(4)
        length, = struct.unpack('!I', length_buf)
        return await reader.read(length)

    @staticmethod
    def create_request(request_id, command, arguments):
        if request_id is None:
            request_id = time.time()
        request = {"id": request_id,
                   "command": command,
                   "arguments": arguments
                   }
        return json.dumps(request).encode("utf-8")

    @staticmethod
    def parse_response(response):
        response = response.decode()
        data = json.loads(response)
        print(response)
        return data["id"], data["status"], data["message"], data["data"]

    def __init__(self, socket_server, link_ip, link_port, pwd):
        self.socket_server = socket_server
        self.link_ip = link_ip
        self.link_port = link_port
        self.pwd = pwd
        self.reader = self.writer = None
        asyncio.run(self.connect())

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.link_ip, self.link_port)
        valid_session, auth_message = await self.send_auth(self.writer)

        while valid_session:
            raw_response = await self.await_receive(self.reader)
            response_id, message, status, data = self.parse_response(raw_response)
            print(raw_response)

    async def send_auth(self, writer):
        auth = self.create_request(None, "login", {"pwd": self.pwd})
        await self.await_write(writer, auth)
        return True, "success"

    async def send_request(self, request_id, command, arguments):
        request = self.create_request(request_id, command, arguments)
        await self.await_write(self.writer, request)
