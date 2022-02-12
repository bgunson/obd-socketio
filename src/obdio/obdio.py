import obd
import socketio
import uvicorn

class OBDio():

    connection = None

    def connect_obd(self, *args, **kwargs):
        """ Create an async connection to vehicle's OBD interface """
        if self.connection is not None:
            self.connection.close()     # Be sure the obd connection is closed 
            del self.connection
        self.connection = obd.Async(*args, **kwargs)
    
    def create_server(self, **kwargs):
        """
            Creates the python-socketio Server instance using same arguments and sets up some default 
            events from the python-OBD API. 
        """
        self.socket = socketio.AsyncServer(**kwargs, async_mode='asgi')
        sio = self.socket

        @sio.event
        async def status(sid):
            await sio.emit('status', self.connection.status(), room=sid)

        @sio.event
        async def is_connected(sid):
            await sio.emit('is_connected', self.connection.is_connected(), room=sid)

        @sio.event
        async def port_name(sid):
            await sio.emit('port_name', self.connection.port_name(), room=sid)

        @sio.event
        async def supports(sid, cmd):
            await sio.emit('supports', self.connection.supports(obd.commands[cmd]), room=sid)

        @sio.event
        async def protocol_id(sid):
            await sio.emit('protocol_id', self.connection.protocol_id(), room=sid)

        @sio.event
        async def protocol_name(sid):
            await sio.emit('protocol_name', self.connection.protocol_name(), room=sid)

        @sio.event
        async def supported_commands(sid):
            await sio.emit('supported_commands', self.connection.supported_commands, room=sid)

        @sio.event
        async def query(sid, cmd):
            await sio.emit('query', self.connection.query(obd.commands[cmd]), room=sid)

        @sio.event
        async def start(sid):
            self.connection.start()

        @sio.event
        async def stop(sid, data):
            self.connection.stop()

        @sio.event
        async def watch(sid, commands):
            self.connection.stop()
            for cmd in commands:
                self.connection.watch(obd.commands[cmd], self.connection.watch_callback)
            self.connection.start()

        @sio.event
        async def unwatch(sid, commands):
            self.connection.stop()
            for cmd in commands:
                self.connection.unwatch(obd.commands[cmd])
            self.connection.start()

        @sio.event
        async def unwatch_all(sid):
            self.connection.stop()
            self.connection.unwatch_all()

        @sio.event
        async def has_name(sid, name):
            await sio.emit('has_name', obd.commands.has_name(name), room=sid)
        
        @sio.event
        async def close(sid):
            self.connection.close()
            await sio.emit('obd_closed')

        return sio

    async def watch_callback(self, response):
        """ Placeholder watch response callback. Should be reassigned with a custom implementation by the user of the module. """
        pass

    def create_event(self, name, handler):
        """ Create custom events by name and custom handler logic """
        sio = self.socket
        @sio.on(name)
        async def custom_event(sid, data=None):
            await handler(sid, data)

    def serve_static(self, static_files):
        """ To set your server's static content before running the server """
        self.static_files = static_files

    def run_server(self, **config):
        """ To start the server on some host:port at a later time so more events can be defined on top of whats already there. """
        
        # Check for static content
        if hasattr(self, 'static_files'):
            static = self.static_files
        else:
            static = None

        app = socketio.ASGIApp(self.socket, static_files=static)
        uvicorn.run(app, **config)