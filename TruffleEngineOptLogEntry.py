from datetime import datetime


class TruffleEngineOptLogEntry:
    def __init__(self, raw, logEventType, engineId, id, name, tier, exec_count, comp_time, ast_size, inline, ir, code_size_in_bytes, code_addr, comp_id, timestamp, source, reason):
        self._raw           = raw
        self._eventType     = logEventType
        self._engineId      = engineId
        self._id            = id
        self._name          = name
        self._tier          = tier
        self._exec_count    = int(exec_count) if exec_count != None else 0
        self._comp_time     = int(comp_time)
        self._ast_size      = ast_size
        self._inline        = inline
        self._ir            = ir
        self._code_size_in_bytes = int(code_size_in_bytes)
        self._code_addr = code_addr
        self._comp_id   = comp_id
        self._timestamp = datetime.strptime(timestamp+"+0000", "%Y-%m-%dT%H:%M:%S.%f%z") # "+0000" to keep all datetimes in same format
        self._source    = source
        self._reason    = reason

    def __str__(self):
        return f"{self._eventType} | {self._raw}"