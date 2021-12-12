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
- <a href="#connecting-to-the-vehicle">Connecting to the Vehicle</a>
- <a href="#configuring-the-server">Configuring the Server</a>
    - <a href="#creating-a-server">Creating a Server</a>
    - <a href="#running-the-server">Running the Server</a>
    - <a href="#serving-static-files">Serving Static Files</a>
    - <a href="#the-watch-callback">The Watch Callback</a>
- <a href="#events">Events</a>
    - <a href="#creating-events">Creating Events</a>
    - <a href="#default-server-events">Default Server Events</a>
- <a href="#json-encodings">JSON Encodings</a>
- <a href="#related">Related Projects</a>

## Connecting to the Vehicle

The OBDIO class iniates the OBD connection to the vehicle. This class extends obd.Async (and therefore obd.OBD) so all aguments are the same, see [OBD connections](https://python-obd.readthedocs.io/en/latest/Connections/) for more arguments.
```
import obdio

io = obdio.OBDio('/dev/ttyUSB0')    # connect to specific serial port
``` 

## Configuring the Server

OBDio currently uses a [Uvicorn](https://www.uvicorn.org/) ASGI (*Asynchronous Server Gateway Interface)* socketio server for handling events asyncronously. Event handlers must be declared `async` and emtting events must be called with the `await` keyword.

### Creating a Server
To create and access the socketio server use `create_server(**kwargs)` which passes its arguments to python-socketio's [Server class](https://python-socketio.readthedocs.io/en/latest/api.html#server-class) giving you control over its behaviour as well as engineIO configuration.

```
import obdio

io = obdio.OBDio()

sio = io.create_server(cors_allowed_origins='*', json=obdio)    # use obdio as the json module for obd support
```
The json parameter can be substituted for your own or the built-in (`import json`) module though it cannot serialize some of the obd types.

### Running the Server

After creating your server socket you can define as many events or background tasks as needed on top of what is already defined by the OBDio class then call `run_server(**config)` to listen on your desired host:port.

Notable Parameters:
- `host` (str) - Use '0.0.0.0' to be accessible on your LAN. 
- `port` (int) - the port the server will listen on

More config args can be found on the Uvicorn [settings page](https://www.uvicorn.org/settings/). Must be called after `create_server`.
```
io.create_server()
io.run_server(host='0.0.0.0', port=48484)
```

### Serving Static Files
Use `serve_static(files)` to confugure the socketio server to serve a files by route, or a folder of static files. See python-socketio [server static files](https://python-socketio.readthedocs.io/en/latest/server.html#serving-static-files) for more info.

-  `files` (dict) - a dictionary of static files to serve by route

```
io = create_server()    # create the server first

io.server_static({
    '/': 'index.html'   # send some index for the route '/'
})

io.run_server()     # run the server after defining the static files
```

### The Watch Callback
When you create an OBDio instance, every OBD command added to the watch loop will be assigned a placeholder callback function called `watch_callback`. It is left for you to define so that data can be handled in your program uniquely. For example, for each response the value could be cached into a dictionary then that entire object streamed over the socket at a lesser rate than `watch_callback` may be fired.

Your custom watch callback will be passed an OBDResponse. If you use `obdio` as your socket JSON serializer, the responses will be encoded correctly when you emit back to the client.
- `response` (obd.OBDResponse) - the obd value that triggered the callback

```
data = {}
def cache_values(response):
    data[response.command] = response 

io.watch_callback = cache_values
```

## Events

When you create and run an OBDio server events are defined for the public python-OBD API which itself is powerful. However based on your use case you may want to add more functionality to the server beyond what is defined. Also, you may wish to override the default implementation of the predefined API to suit your needs.

### Creating Events

One way to create custom or override events is to use `create_event(name, handler)`.

- `name` (string) - the name of a custom or overriden event
- `async handler(sid, data)` (function) - the custom event handler - must be async

You are able to create custom events, or override the defaults with custom behaivour.
```
sio = io.create_server()   # call create server first to access the socket

async def custom_handler(sid, data):    # handlers must be async
    await sio.emit('custom', data)      # any emits must be awaited

io.create_event('custom_event', custom_handler)

io.run_server(port)     # lastly call run_server
```
Or, you can use the [@sio.event](https://python-socketio.readthedocs.io/en/latest/server.html#defining-event-handlers) decorator allowing you to create events as you would with an ASGI server.

```

@sio.event
async def watch(sid, cmd):
    await sio.emit('event')     # emits must be awaited

io.run_server(48484)
```

### Default Server Events
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

2. To query a command, it must be `watch`ed first

See the python-OBD [documentation](https://python-obd.readthedocs.io/en/latest/) for expected behaviour of the default events.

## JSON Encodings

Currently the JSON encodings for the python-OBD types provide minimal data excluding unnessacary and non-human readable values to keep payload size smaller when emitting back to a client. 

### OBDCommand
- `name` (string) - human readable representation of a PID, all caps
- `desc` (string) - human readable description of the command

Example:
```
{
    "name": "SPEED",
    "desc": "Vehicle Speed"
}
```

### OBDResponse
- `value` (any) - the response value: numeric, array
- `command` (OBDCommand) - the command the response is for
- `time` (number) - Unix timestamp (seconds) of the response
- `unit` (string) - the unit of the response value. Non-numeric responses (dtcs, o2 sensors, etc) units will be represented as their type such as `"<class 'tuple'>"` while numeric ones will be a literal representing their unit from the [obd unit registry](https://github.com/brendan-w/python-OBD/blob/master/obd/UnitsAndScaling.py) (pint value). 

Example:
```
{
    "value": 1500,
    "command": {
        "name": "RPM",
        "desc": "Engine RPM"
    },
    "time": 1639266637.0963762,
    "unit": "revolutions_per_minute"
}
```
OBDResponse - Status Example:
```
{
    "value": {
        "MIL": false,
        "DTC_COUNT": 0,
        "ignition_type": "spark"
    },
    "command": {
        "name": "STATUS",
        "desc": "Status since DTCs cleared"
    },
    "time": 1639341509.038382,
    "unit": "<class 'obd.OBDResponse.Status'>"
}
```
Note the value is another object and unit describes the type of the response since it is not measurable.


## Related 
- [python-OBD](https://github.com/brendan-w/python-OBD)
- [socket.io](https://github.com/socketio/socket.io)
- [python-socketio](https://github.com/miguelgrinberg/python-socketio)
- [ELM327-Simulator](https://github.com/Ircama/ELM327-emulator)
- [Uvicorn](https://github.com/encode/uvicorn)