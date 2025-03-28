from dataclasses import dataclass
from datetime import datetime

from .LogEventType import LogEventType


@dataclass
class HotSpotLogEntry:
    _raw: str
    log_event_type: LogEventType
    comp_id: int
    timestamp: datetime

    def __str__(self):
        return f"{self.log_event_type} | {self._raw}"
