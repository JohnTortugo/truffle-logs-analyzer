from enum import Enum

class LogEventType(Enum):
    Start                 = 1
    Done                  = 2
    Deoptization          = 3
    Invalidation          = 4
    Enqueued              = 5
    Dequeued              = 6
    Failed                = 7
    TransferToInterpreter = 8
    CacheFlushing         = 9