import re
from datetime import datetime, timezone
from typing import Optional

from .HotSpotLogEntry import HotSpotLogEntry
from .LogEventType import LogEventType

pattern = r'\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+\d{4})\]\s*\*flushing.*nmethod\s+(\d+)/.*'


class ParseHotspotLogEntry:
    def __init__(self, log_line: str):
        self._entry = self._parse_code_cache_entry(log_line.strip())

    def entry(self) -> Optional[HotSpotLogEntry]:
        return self._entry

    def _parse_code_cache_entry(self, log_line: str) -> Optional[HotSpotLogEntry]:
        return self._parse_code_cache_flushing_entry(log_line)

    def _parse_code_cache_flushing_entry(self, log_line: str) -> Optional[HotSpotLogEntry]:
        match = re.search(pattern, log_line)
        if match:
            timestamp = match.group(1)
            return HotSpotLogEntry(_raw=log_line,
                                   log_event_type=LogEventType.CacheFlushing,
                                   comp_id=int(match.group(2)),
                                   timestamp=datetime.fromisoformat(timestamp[:-2] + ":" + timestamp[-2:]).astimezone(timezone.utc))
        else:
            return None