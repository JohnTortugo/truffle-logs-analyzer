from enum import Enum

class ReplCommand(Enum):
    Histogram   = 1
    Stats       = 2
    CompRate    = 3
    CompParetto = 4
    CallId      = 5
    Hotspots    = 6
    FileName    = 7
    Quit        = 8