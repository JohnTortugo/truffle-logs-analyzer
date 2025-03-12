from enum import Enum


class LogEventType(Enum):
    Start          = 1
    Done           = 2
    Deoptization   = 3
    Invalidation   = 4
    Unqueue        = 5
    Failed         = 6
    CacheFlushing  = 7