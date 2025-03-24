import re
from typing import Optional

from HotSpotLogEntry import HotSpotLogEntry
from LogEventType import LogEventType


class ParseHotspotLogEntry:
    def __init__(self, log_line: str):
        self._entry = self._parse_code_cache_entry(log_line.strip())

    def entry(self) -> Optional[HotSpotLogEntry]:
        return self._entry

    def _parse_code_cache_entry(self, log_line: str) -> Optional[HotSpotLogEntry]:
        return self._parse_code_cache_flushing_entry(log_line)

    def _parse_code_cache_flushing_entry(self, log_line: str) -> Optional[HotSpotLogEntry]:
        pattern = r'\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+\d{4})\]\s*\*flushing.*nmethod\s+(\d+)/.*'

        match = re.search(pattern, log_line)
        if match:
            timestamp = match.group(1)
            return HotSpotLogEntry(log_line,
                                   LogEventType.CacheFlushing,
                                   int(match.group(2)),
                                   timestamp[:-2] + ":" + timestamp[-2:]) # timestamp from logs omits colon, this injects it
        else:
            return None