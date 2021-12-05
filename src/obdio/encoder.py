import json
import obd

class OBDEncoder(json.JSONEncoder):
    def default(self, o):

        if isinstance(o, obd.OBDStatus):
            return ""

        if isinstance(o, obd.ECU):
            return ""

        if isinstance(o, obd.OBDResponse):
            if o.is_null():
                return json.dumps(None)
            else:
                return json.dumps({
                    'value': o.value,
                    'command': o.command,
                    'message': o.messages,
                    'time': o.time,
                    'unit': o.unit
                })
                
        if isinstance(o, obd.OBDCommand):
            return json.dumps({
                'name': o.name,
                'commandd': o.command,
                'desc': o.desc,
                'bytes': o.bytes,
                'decode': o.decode,
                'ecu': o.ecu,
                'fast': o.fast,
                'header': o.header
            })

        return json.JSONEncoder.default(self, o)
