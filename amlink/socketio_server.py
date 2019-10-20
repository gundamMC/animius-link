import asyncio
import threading
import time

import socketio
import uvicorn

import amlink


class SocketIOServer:

    def __init__(self):

        self.sio = socketio.AsyncServer(async_mode='asgi')

        # wrap with ASGI application
        self.app = socketio.ASGIApp(self.sio)
        self.engine = None
        self.pending_requests = {}

        # create a Socket.IO server
        # self.sio = socketio.Server()
        #
        # # wrap with a WSGI application
        # self.app = socketio.WSGIApp(self.sio)

        @self.sio.event
        async def auth(sid, data):
            print('==========')
            print(data)
            print('==========')

            if 'username' not in data or 'password' not in data:
                return False

            user = amlink.users.get_user(data['username'])

            if user is None or not user.checkPassword(data['password']):
                return 'The username or password is incorrect'

            await self.sio.save_session(sid, {'username': data['username']})
            return True

        @self.sio.event
        async def register(sid, data):
            if amlink.config['allow_registration']:
                if 'username' in data and 'password' in data:
                    amlink.users.create_user(data['username'], data['password'])
                    await self.sio.save_session(sid, {'username': data['username']})

                    return True
                else:
                    return 'Username and password must be included'
            else:
                return 'Registration is disabled'

        @self.sio.event
        async def waifu_list(sid, data):
            session = await self.sio.get_session(sid)
            self.pending_requests[data['id']] = [sid, True, session['username']]
            await self.engine.send_request(time.time(), 'getWaifu', {}, False)
            return True

        @self.sio.event
        async def message(sid, data):
            session = await self.sio.get_session(sid)
            self.pending_requests[data['id']] = [sid, True, session['username']]
            await self.engine.send_request(time.time(), 'waifuPredict', data['arguments'], True)

        @self.sio.event
        async def connect(sid, environ):
            print('connected!', sid)

    def start(self, host, port, engine_ip, engine_port, pwd):
        self.engine = amlink.connect_engine.Connect(engine_ip, engine_port, pwd, self, True)
        engine_thread = threading.Thread(target=asyncio.run, args=(self.engine.connect(),), daemon=True)
        engine_thread.start()
        uvicorn.run(self.app, host=host, port=port)

        # eventlet.wsgi.server(eventlet.listen((host, port)), self.app)
