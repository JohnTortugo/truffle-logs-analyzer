from enum import Enum

class ReplCommand(Enum):
    Histogram   = 1
    Stats       = 2
    CompRate    = 3
    CompParetto = 4
    CallId      = 5
    FileName    = 6
    Quit        = 7