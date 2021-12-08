# obd-socketio

Quickly create a [python-socketio](https://github.com/miguelgrinberg/python-socketio) server with events corresponding to the [python-OBD](https://github.com/brendan-w/python-OBD) API. Ideal for controlling an Async connection to a vehicle from a JavaScript socketio client. The module provides default events which correspond to python-OBD methods as well as JSON encoding for its types.

An example use case would be to use the server on a wireless hotspot enabled Raspberry Pi and be able to interact with the connection from another device in a browser. You can use the default events which will behave as python-OBD does or build your own custom websocket/OBD2 API.

## Installation
```
pip install obd-socketio
```

## Basic Usage
```
import obdio

# Initiate connection to the vehicle
io = obdio.OBDio()

# Create the server socket
io.create_server()  

# Start the server
io.run_server()
```

## API

- Connecting to the Vehicle with OBDio  
    - [OBDio class](#obdio-class)
- Configuring the Server
    - [create_server()](#create-server)
    - [run_server()](#run-server)
    - [serve_static()](#serve-static)
- Events
    - [create_event()](#create-event)
    - [watch_callback()](#watch-callback)
    - [Default Server Events](#def-events)


## <a name="obdio-class" /> OBDio class 
Initiaties the OBD connection to the vehicle. This class extends obd.Async (and therefore obd.OBD) so all aguments are the same, see [OBD connections](https://python-obd.readthedocs.io/en/latest/Connections/) for more args.
```
import obdio

io = obdio.OBDio('/dev/ttyUSB0')    # connect to specific serial port
``` 

## <a name="create-server"/> create_server(**kwargs)
- Returns the server socket

Creates the socketio server instance and gives you access to the socket after being called. `create_server()` passes its arguments to python-socketio's [Server class](https://python-socketio.readthedocs.io/en/latest/api.html#server-class) giving you control over its behaviour as well as engineIO configuration. For example
```
import obdio

io = obdio.OBDio()

sio = io.create_server(cors_allowed_origins='*', json=obdio)    # use obdio as the json module for obd support
```
The json parameter can be substituted for your own or the built-in (`import json`) module though it cannot serialize some of the obd types.

## <a name="run-server"/> run_server(**config)
Notable Parameters:
- `host` (str) - Use '0.0.0.0' to be accessible on your LAN. 
- `port` (int) - the port the server will listen on

More config args can be found on the Uvicorn [settings page](https://www.uvicorn.org/settings/). Must be called after `create_server`.
```
io.create_server()
io.run_server(host='0.0.0.0', port=48484)
```

## <a name="serve-static"/> serve_static(files)
-  `files` (dict) - a list of static files to serve by route

Confugure the socketio server to server static files, or a folder of static files. See python-socketio [server static files](https://python-socketio.readthedocs.io/en/latest/server.html#serving-static-files) for more info.
```
io = create_server()    # create the server first

io.server_static({
    '/': 'index.html'   # send some index for the route '/'
})

io.run_server()     # run the server after defining the static files
```

## <a name="create-event"/> create_event(name, handler)
- `name` (string) - the name of a custom or overriden event
- `async handler(sid, data)` (function) - the custom event handler

You are able to create custom events, or override the defaults with custom behaivour.
```
sio = io.create_server()   # call create server first to access the socket

async def custom_handler(sid, data):    # handlers must be async
    await sio.emit('custom', data)      # must await socket emits

io.create_event('custom_event', custom_handler)

io.run_server(port)     # lastly call run_server
```
To override default events you can use the above method or use the [@sio.event](https://python-socketio.readthedocs.io/en/latest/server.html#defining-event-handlers) decorator
```

@sio.event
async def watch(sid, cmd):
    await sio.emit('event')     # emits must be awaited

io.run_server(48484)
```

## <a name="watch-callback"/> watch_callback(response)
- `response` (obd.OBDResponse) - the obd value that triggered the callback

Out of the box, when commands are watched they are all given the same callback `watch_callback` which does not implement anything. It is left for you to define so that data can be handled in your program uniquely. For example, for each response the value could be cached into a dictionary then that entire object streamed over the socket at a lesser rate than `watch_callback` may be fired.

```
data = {}
def cache_values(response):
    data[response.command] = response.value

io.watch_callback = cache_values
```

## <a name="def-events"/> Default Server Events
On creation of an OBDio server most of the python-OBD API is exposed through events of the same name as its functions. The server will handle the event then respond with data (if any) using the same event name.

| **Event Name**        | **Argument Type**          | **Response Type** |
|-----------------------|----------------------------|-------------------|
| 'status'              | None                       | string            |
| 'is_connected'        | None                       | boolean           |
| 'protocol_name'       | None                       | string            |
| 'protocol_id'         | None                       | string            |
| 'port_name'           | None                       | string            |
| 'supports'            | string<sup>1               | boolean           |
| 'supported_commands'  | None                       | object            |
| 'query' <sup>2        | string<sup>1               | N/A               |
| 'start'               | None                       | N/A               |
| 'watch'               | (string or string[])<sup>1 | N/A               |
| 'unwatch'             | (string or string[])<sup>1 | N/A               |
| 'unwatch_all'         | None                       | N/A               |
| 'has_name'            | string<sup>1               | boolean           |
| 'close'               | None                       | N/A               |

1. Arg is a string (or list of) OBD command by name i.e. 'RPM', 'SPEED'. See the OBD [Command Tables](https://python-obd.readthedocs.io/en/latest/Command%20Tables/).

2. To query a command, it must be 'watched' first

See the python-OBD [documentation](https://python-obd.readthedocs.io/en/latest/) for expected behaviour of the default events.


