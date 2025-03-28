import re
from datetime import datetime, timezone
from typing import Optional

from .LogEventType import LogEventType
from .TruffleEngineOptLogEntry import TruffleEngineOptLogEntry

pattern = r'\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}\+\d{4})\]\s*\*flushing.*nmethod\s+(\d+)/.*'


class ParseHotspotLogEntry:
    def __init__(self, log_line: str):
        self._entry = self._parse_code_cache_entry(log_line.strip())

    def entry(self) -> Optional[TruffleEngineOptLogEntry]:
        return self._entry

    def _parse_code_cache_entry(self, log_line: str) -> Optional[TruffleEngineOptLogEntry]:
        return self._parse_code_cache_flushing_entry(log_line)

    def _parse_code_cache_flushing_entry(self, log_line: str) -> Optional[TruffleEngineOptLogEntry]:
        match = re.search(pattern, log_line)
        if match:
            timestamp = match.group(1)
            return TruffleEngineOptLogEntry(
                _raw=log_line,
                log_event_type=LogEventType.CacheFlushing,
                engine_id=None,
                id=None,
                name=None,
                tier=None,
                exec_count=None,
                threshold=None,
                priority=None,
                rate=None,
                queue_size=None,
                queue_change=None,
                queue_load=None,
                queue_time=None,
                comp_time=None,
                ast_size=None,
                inline=None,
                ir=None,
                code_size_in_bytes=None,
                code_addr=None,
                comp_id=int(match.group(2)),
                timestamp = datetime.fromisoformat(timestamp[:-2] + ":" + timestamp[-2:]).astimezone(timezone.utc),
                source = None,
                reason = None,
            )
        else:
            return None