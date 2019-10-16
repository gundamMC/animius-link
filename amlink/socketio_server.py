import socketio
import uvicorn

# create a Socket.IO server
import amlink


class SocketIOServer:

    def __init__(self, network):

        self.sio = socketio.AsyncServer(async_mode='asgi')

        # wrap with ASGI application
        self.app = socketio.ASGIApp(self.sio)

        # create a Socket.IO server
        # self.sio = socketio.Server()
        #
        # # wrap with a WSGI application
        # self.app = socketio.WSGIApp(self.sio)

        self.network = network

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
        async def waifuList(sid, data):
            session = await self.sio.get_session(sid)
            self.network.toEngine(data['id'], sid, session['username'], 'getWaifu', {}, 'waifuList')
            return True

        @self.sio.event
        async def message(sid, data):
            session = await self.sio.get_session(sid)
            self.network.toEngine(data['id'], sid, session['username'], 'waifuPredict', data['arguments'], True)

        @self.sio.event
        async def connect(sid, environ):
            print('connected!', sid)

    def start(self, host, port):
        uvicorn.run(self.app, host='192.168.0.50', port=port)
        # eventlet.wsgi.server(eventlet.listen((host, port)), self.app)
