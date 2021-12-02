import obd
import socketio
import eventlet

class OBDio(obd.Async):

    def createServer(self, **kwargs):
        self.socket = socketio.Server(**kwargs)
        sio = self.socket

        @sio.event
        def connect(sid, envron, auth):
            print("client connected", self.status())

        @sio.event
        def status(sid, data):
            self.sio.emit('status', self.status(), room=sid)

        @sio.event
        def is_connected(sid):
            self.sio.emit('is_connected', self.is_connected(), room=sid)

        @sio.event
        def stop(sid, data):
            self.stop()

        @sio.event
        def close(sid):
            self.close()

        @sio.event
        def query(sid, cmd):
            self.sio.emit('obd_query', self.query(cmd), room=sid)

        @sio.event
        def watch(sid, pids):
            pids = list(pids)
            for cmd in pids:
                self.watch(obd.commands[cmd], self.watch_callback)

        @sio.event
        def unwatch(sid, pid):
            self.unwatch(pid)

        @sio.event
        def unwatch_all(sid):
            self.unwatch_all()

    def listen(self, port):
        app = socketio.WSGIApp(self.socket)
        eventlet.wsgi.server(eventlet.listen(('127.0.0.1', port)), app)

    def watch_callback(response):
        pass

    def createEvent(self, name, handler):
        sio = self.socket
        @sio.on(name)
        def custom_event(sid, data=None):
            handler(sid, data)