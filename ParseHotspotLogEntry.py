from HotSpotLogEntry import HotSpotLogEntry
from LogEventType import LogEventType


class ParseHotspotLogEntry:
    def __init__(self, logLine):
        self._entry = None
        logLine = logLine.strip()

        if logLine.find("*flushing ") >= 0:
            self._entry = self.parseCodeCacheEntry(logLine);

    def entry(self):
        return self._entry

    def parseCodeCacheEntry(self, logLine):
        if logLine.find("*flushing ") >= 0 :
            return self.parseCodeCacheFlushingEntry(logLine)
        #else:
        #    print(f"Ignoring this codecache line: {logLine}")
        return None

    def parseCodeCacheFlushingEntry(self, logLine):
        start = logLine.find("[")
        end = logLine.find("] *flushing", start+1)
        hotspot_timestamp = logLine[start+1:end]

        pattern = "nmethod "
        start = logLine.find(pattern)
        end = logLine.find("/", start+1)
        hotspot_comp_id = int(logLine[start+len(pattern):end])

        return HotSpotLogEntry(logLine,
                                LogEventType.CacheFlushing,
                                hotspot_comp_id,
                                hotspot_timestamp)