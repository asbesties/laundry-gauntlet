from requests import get
from json import loads
from markupsafe import escape
from data import *

class Mach(object):
    def __init__(self, _id:int, _type:str, doorClosed:bool, mode:str, available:bool, notAvailableReason:str, timeLeft:int) -> None:
        self._id = _id
        self._ty = _type
        self.doorClosed = doorClosed
        self.mode = mode
        self.available = available
        self.notAvailableReason = notAvailableReason
        self.timeLeft = timeLeft
    
    def __str__(self) -> str:
        return f'{self._ty[0]}{self._id}: {self.timeLeft}min {self.doorClosed * "door-closed"} {self.available * "available"} {self.notAvailableReason}'

class Hall(object):
    def __init__(self, name:str, machs:list) -> None:
        self.name:str = name
        self.machs:list = machs
    
    def __str__(self) -> str:
        return f"{self.name} hall: {str([str(x) for x in self.machs])}"

def machines(hall):
    machines = loads(get(api + halls[hall]).text)
    return machines

def get_mach(mach, hall) :
    mech = machines(hall)["machines"]
    mach = int(mach)
    md = dict()
    for m in mech:
        md[m["stickerNumber"]] = m
    if mach in md.keys():
        return md[mach]
    else: return ""

def mach_api(hall):
    return Hall(hall, [Mach(m["stickerNumber"], m["type"], m["doorClosed"], m["mode"], m["available"], m["notAvailableReason"], m["timeRemaining"]) for m in machines(hall)["machines"]])