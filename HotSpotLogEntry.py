from datetime import datetime

class HotSpotLogEntry:
    def __init__(self, raw, logEventType, hotspotCompId, timestamp):
        self._raw       = raw
        self._tier      = ""
        self._eventType = logEventType
        self._comp_id  = hotspotCompId
        self._timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
        #self._timestamp = datetime.strptime("2055-01-01T23:59:59", "%Y-%m-%dT%H:%M:%S.%f%z")

    def __str__(self):
        return f"{self._eventType} | {self._raw}"