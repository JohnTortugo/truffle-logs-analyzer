from datetime import datetime

from LogEventType import LogEventType


class HotSpotLogEntry:
    def __init__(self,
                 raw: str,
                 logEventType: LogEventType,
                 hotspotCompId: int,
                 timestamp: str):
        self._raw: str   = raw
        self._eventType: LogEventType = logEventType
        self._comp_id: int = hotspotCompId
        self._timestamp: datetime = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
        self._tier = ""

    def __str__(self):
        return f"{self._eventType} | {self._raw}"