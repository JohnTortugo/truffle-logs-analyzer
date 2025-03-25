from datetime import datetime, timezone

from .LogEventType import LogEventType


class HotSpotLogEntry:
    def __init__(self,
                 raw: str,
                 logEventType: LogEventType,
                 hotspotCompId: int,
                 timestamp: str):
        self._raw: str   = raw
        self._eventType: LogEventType = logEventType
        self._comp_id: int = hotspotCompId
        self._timestamp: datetime = datetime.fromisoformat(timestamp).astimezone(timezone.utc)
        self._tier = ""

    def __str__(self):
        return f"{self._eventType} | {self._raw}"