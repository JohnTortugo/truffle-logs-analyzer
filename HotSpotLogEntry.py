class HotSpotLogEntry:
    def __init__(self, raw, logEventType, hotspotCompId, timestamp):
        self._raw       = raw
        self._tier      = ""
        self._eventType = logEventType
        self._hotspotCompId  = hotspotCompId
        self._timestamp = timestamp #datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")

    def __str__(self):
        return f"{self._eventType} | {self._raw}"