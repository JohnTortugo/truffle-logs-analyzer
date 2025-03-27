from datetime import datetime
from typing import Optional

from .LogEventType import LogEventType


class TruffleEngineOptLogEntry:
    def __init__(self,
                 raw: str,
                 log_event_type: LogEventType,
                 engine_id: int,
                 id: int,
                 name: str,
                 tier: Optional[int],
                 exec_count: Optional[int],
                 threshold: Optional[int],
                 priority: Optional[int],
                 rate: Optional[float],
                 queue_size: Optional[int],
                 queue_change: Optional[int],
                 queue_load: Optional[float],
                 queue_time: Optional[int],
                 comp_time: Optional[int],
                 ast_size: Optional[int],
                 inline: Optional[str],
                 ir: Optional[str],
                 code_size_in_bytes: Optional[int],
                 code_addr: Optional[str],
                 comp_id: Optional[int],
                 timestamp: datetime,
                 source: str,
                 reason: Optional[str]):
        self._raw: str = raw
        self._eventType: LogEventType = log_event_type
        self._engineId: int = engine_id
        self._id: int = id
        self._name: str = name
        self._tier: Optional[int] = tier
        self._exec_count: Optional[int] = exec_count
        self._threshold: Optional[int] = threshold
        self._priority: Optional[int] = priority
        self._rate: Optional[float] = rate
        self._queue_size: Optional[int] = queue_size
        self._queue_change: Optional[int] = queue_change
        self._queue_load: Optional[float] = queue_load
        self._queue_time: Optional[int] = queue_time
        self._comp_time: Optional[int]= comp_time
        self._ast_size:  Optional[int] = ast_size
        self._inline: Optional[str] = inline
        self._ir: Optional[str] = ir
        self._code_size_in_bytes: Optional[int] = code_size_in_bytes
        self._code_addr: Optional[str] = code_addr
        self._comp_id: Optional[int] = comp_id
        self._timestamp: datetime = timestamp
        self._source: str = source
        self._reason: Optional[str] = reason

    def __str__(self):
        return f"{self._eventType} | {self._raw}"