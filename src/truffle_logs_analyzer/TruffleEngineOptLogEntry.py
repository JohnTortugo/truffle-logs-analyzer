from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .LogEventType import LogEventType


@dataclass
class TruffleEngineOptLogEntry:
    _raw: str
    log_event_type: LogEventType
    engine_id: Optional[int]
    id: Optional[int]
    name: Optional[str]
    tier: Optional[int]
    exec_count: Optional[int]
    threshold: Optional[int]
    priority: Optional[int]
    rate: Optional[float]
    queue_size: Optional[int]
    queue_change: Optional[int]
    queue_load: Optional[float]
    queue_time: Optional[int]
    comp_time: Optional[int]
    ast_size: Optional[int]
    inline: Optional[str]
    ir: Optional[str]
    code_size_in_bytes: Optional[int]
    code_addr: Optional[str]
    comp_id: Optional[int]
    timestamp: datetime
    source: Optional[str]
    reason: Optional[str]

    def __str__(self):
        return f"{self.log_event_type} | {self._raw}"