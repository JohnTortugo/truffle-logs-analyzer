from enum import Enum

class LogEventType(Enum):
    Start                 = 1
    Done                  = 2
    Deoptimization        = 3
    Invalidation          = 4
    Enqueued              = 5
    Dequeued              = 6
    Failed                = 7
    Flushed               = 8
    TransferToInterpreter = 9
    CacheFlushing         = 10
    Disabled              = 11
    Enabled               = 12
