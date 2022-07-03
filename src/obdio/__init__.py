from .obdio import OBDio
from .encoder import OBDEncoder
import json

def loads(*args, **kwargs):
    return json.loads(*args, **kwargs)

def dumps(*args, **kwargs):
    return json.dumps(*args, **kwargs, cls=OBDEncoder)

def load(*args, **kwargs):
    return json.load(*args, **kwargs)

def dump(*args, **kwargs):
    return json.dump(*args, **kwargs, cls=OBDEncoder)
