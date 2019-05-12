import asyncio

import uvicorn

import socketio

# create a Socket.IO server
import amlink

sio = socketio.AsyncServer(async_mode='asgi')

# wrap with ASGI application
app = socketio.ASGIApp(sio)

users = {}

class MyCustomNamespace(socketio.AsyncNamespace):

    # def __init__(self):
    #     super().__init__()
    #
    #     self.users = []

    async def on_connect(self, sid, environ):
        print(sid)
        print(environ)
        users[sid] = None

    async def on_disconnect(self, sid):
        pass

    async def on_auth(self, sid, data):
        print('==========')
        print(data)
        print('==========')

        if 'username' not in data or 'password' not in data:
            return False

        user = amlink.users.get_user(data['username'])

        if user is None or not user.check_password(data['password']):
            return 'The username or password is incorrect'

        return True


sio.register_namespace(MyCustomNamespace())

uvicorn.run(app, host='127.0.0.1', port=5000)
