import re
from datetime import datetime, timezone
from typing import Optional

from LogEventType import LogEventType
from TruffleEngineOptLogEntry import TruffleEngineOptLogEntry

OPT_REGEX = re.compile(r'^\[engine] opt ([\w.]+)\s+engine=(\d+)\s+id=(\d+)(.*)')
TIER_REGEX = re.compile(r'^Tier\s+(\d)')
PRIORITY_REGEX = re.compile(r'^Priority\s+(\d+)')
RATE_REGEX = re.compile(r'Rate\s+(\d*\.?\d+|NaN)')
QUEUE_STATS_REGEX = re.compile(r'^Queue:\s+Size\s+(\d+)\s+Change\s+([+-]?\d+)\s+Load\s+(\d*\.?\d+)\s+Time\s+(\d+)us')
TIMESTAMP_REGEX = re.compile(r'^UTC\s+(\d\d\d\d-.*)')
THRESHOLDS_REGEX = re.compile(r'Count/Thres\s+(\d+)/\s+(\d+)')
TIME_REGEX = re.compile(r'^Time\s+(\d+).*')
AST_REGEX = re.compile(r'^AST\s+(\d+)')
INLINE_REGEX = re.compile(r'^(Inlined\s+\d+Y\s+\d+N)')
IR_REGEX = re.compile(r'(IR\s+\d+/\s*\d+)')
CODE_SIZE_REGEX = re.compile(r'^CodeSize\s+(\d+)')
ADDRESS_REGEX = re.compile(r'^Addr\s+(.*)')
COMP_ID_REGEX = re.compile(r'CompId\s+(\d+)')


class ParseTruffleEngineOptLogEntry:
    def __init__(self, log_line: str):
        self._entry = self.parse(log_line)

    def entry(self) -> Optional[TruffleEngineOptLogEntry]:
        return self._entry

    def parse(self, log_line: str) -> Optional[TruffleEngineOptLogEntry]:
        # FIXME...parse tregex
        if "tregex" in log_line:
            return None

        segments = [s.strip() for s in log_line.split("|")]
        opt = self.match(segments[0], OPT_REGEX, 4, "Operation")[0]

        if opt == 'queued':
            if not len(segments) == 6: raise ValueError(f"opt queued should have 6 segments, got {segments}")
            return self.queued(log_line, segments)
        elif opt == 'start':
            if not len(segments) == 7: raise ValueError(f"opt start should have 7 segments, got {segments}")
            return self.start(log_line, segments)
        elif opt == 'done':
            if not len(segments) == 11: raise ValueError(f"opt done should have 11 segments, got {segments}")
            return self.done(log_line, segments)
        elif opt == 'deopt':
            if not len(segments) == 4: raise ValueError(f"opt deopt should have 4 segments, got {segments}")
            return self.deopt(log_line, segments)
        elif opt == 'inval.':
            if not len(segments) == 4: raise ValueError(f"opt inval. should have 4 segments, got {segments}")
            return self.inval(log_line, segments)
        elif opt == 'unque.':
            if not len(segments) == 7: raise ValueError(f"opt unque. should have 7 segments, got {segments}")
            return self.unque(log_line, segments)
        elif opt == 'failed':
            if not len(segments) == 6: raise ValueError(f"opt failed should have 6 segments, got {segments}")
            return self.failed(log_line, segments)
        else:
            raise ValueError(f"Unknown option '{opt}'")

    def match(self, s: str, regex: re.Pattern[str], length: int, identifier: str) -> list[str]:
        match = regex.match(s)
        if match:
            segments = [s.strip() for s in match.groups()]
            if len(segments) == length:
                return segments

        raise ValueError(f"Failed to match {identifier} in '{s}'")

    def parse_timestamp(self, s: str) -> datetime:
        return datetime.fromisoformat(
            self.match(s, TIMESTAMP_REGEX, 1, 'Timestamp')[0]).astimezone(timezone.utc)

    def queued(self, log_line: str, segments: list[str]) -> TruffleEngineOptLogEntry:
        identifiers = self.match(segments[0], OPT_REGEX, 4, "Operation")
        comp_thresholds = self.match(segments[2], THRESHOLDS_REGEX, 2, 'CompThresholds')
        queue_stats = self.match(segments[3], QUEUE_STATS_REGEX, 4, 'QueueStats')

        return TruffleEngineOptLogEntry(
            raw=log_line,
            log_event_type=LogEventType.Enqueued,
            engine_id=int(identifiers[1]),
            id=int(identifiers[2]),
            name=identifiers[3],
            tier=int(self.match(segments[1], TIER_REGEX, 1, "Tier")[0]),
            exec_count=int(comp_thresholds[0]),
            threshold=int(comp_thresholds[1]),
            queue_size=int(queue_stats[0]),
            queue_change=int(queue_stats[1]),
            queue_load=float(queue_stats[2]),
            queue_time=int(queue_stats[3]),
            priority=None,
            rate=None,
            comp_time=None,
            ast_size=None,
            inline=None,
            ir=None,
            code_size_in_bytes=None,
            code_addr=None,
            comp_id=None,
            timestamp=self.parse_timestamp(segments[-2]),
            source=segments[-1],
            reason=None,
        )


    def start(self, log_line: str, segments: list[str]) -> TruffleEngineOptLogEntry:
        identifiers = self.match(segments[0], OPT_REGEX, 4, "Operation")
        queue_stats = self.match(segments[4], QUEUE_STATS_REGEX, 4, 'QueueStats')

        return TruffleEngineOptLogEntry(
            raw=log_line,
            log_event_type=LogEventType.Start,
            engine_id=int(identifiers[1]),
            id=int(identifiers[2]),
            name=identifiers[3],
            tier=int(self.match(segments[1], TIER_REGEX, 1, 'Tier')[0]),
            exec_count=None,
            threshold=None,
            priority=int(self.match(segments[2], PRIORITY_REGEX, 1, 'Priority')[0]),
            rate=float(self.match(segments[3], RATE_REGEX, 1, 'Rate')[0]),
            queue_size=int(queue_stats[0]),
            queue_change=int(queue_stats[1]),
            queue_load=float(queue_stats[2]),
            queue_time=int(queue_stats[3]),
            comp_time=None,
            ast_size=None,
            inline=None,
            ir=None,
            code_size_in_bytes=None,
            code_addr=None,
            comp_id=None,
            timestamp=self.parse_timestamp(segments[5]),
            source=segments[6],
            reason=None,
        )


    def done(self, log_line: str, segments: list[str]) -> TruffleEngineOptLogEntry:
        identifiers = self.match(segments[0], OPT_REGEX, 4, "Operation")
        inlines = self.match(segments[4], INLINE_REGEX, 1, 'Inlines')
        irs = self.match(segments[5], IR_REGEX, 1, 'IR')

        return TruffleEngineOptLogEntry(
            raw=log_line,
            log_event_type=LogEventType.Done,
            engine_id=int(identifiers[1]),
            id=int(identifiers[2]),
            name=identifiers[3],
            tier=int(self.match(segments[1], TIER_REGEX, 1, 'Tier')[0]),
            exec_count=None,
            threshold=None,
            priority=None,
            rate=None,
            queue_size=None,
            queue_change=None,
            queue_load=None,
            queue_time=None,
            comp_time=int(self.match(segments[2], TIME_REGEX, 1, 'CompTime')[0]),
            ast_size=int(self.match(segments[3], AST_REGEX, 1, 'AST')[0]),
            inline=inlines[0],
            ir=irs[0],
            code_size_in_bytes=int(self.match(segments[6], CODE_SIZE_REGEX, 1, 'CodeSize')[0]),
            code_addr=self.match(segments[7], ADDRESS_REGEX, 1, 'Address')[0],
            comp_id=int(self.match(segments[8], COMP_ID_REGEX, 1, 'CompId')[0]),
            timestamp=self.parse_timestamp(segments[9]),
            source=segments[10],
            reason=None,
        )

    def deopt(self, log_line: str, segments: list[str]) -> TruffleEngineOptLogEntry:
        identifiers = self.match(segments[0], OPT_REGEX, 4, "Operation")
        return TruffleEngineOptLogEntry(
            raw=log_line,
            log_event_type=LogEventType.Deoptization,
            engine_id=int(identifiers[1]),
            id=int(identifiers[2]),
            name=identifiers[3],
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
            comp_id=None,
            timestamp=self.parse_timestamp(segments[2]),
            source=segments[3],
            reason=None,
        )


    def inval(self, log_line: str, segments: list[str]) -> TruffleEngineOptLogEntry:
        identifiers = self.match(segments[0], OPT_REGEX, 4, "Operation")
        return TruffleEngineOptLogEntry(
            raw=log_line,
            log_event_type=LogEventType.Invalidation,
            engine_id=int(identifiers[1]),
            id=int(identifiers[2]),
            name=identifiers[3],
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
            comp_id=None,
            timestamp=self.parse_timestamp(segments[1]),
            source=segments[2],
            reason=segments[3],
        )


    def unque(self, log_line: str, segments: list[str]) -> TruffleEngineOptLogEntry:
        identifiers = self.match(segments[0], OPT_REGEX, 4, "Operation")
        comp_thresholds = self.match(segments[2], THRESHOLDS_REGEX, 2, 'CompThresholds')
        queue_stats = self.match(segments[3], QUEUE_STATS_REGEX, 4, 'QueueStats')

        return TruffleEngineOptLogEntry(
            raw=log_line,
            log_event_type=LogEventType.Dequeued,
            engine_id=int(identifiers[1]),
            id=int(identifiers[2]),
            name=identifiers[3],
            tier=int(self.match(segments[1], TIER_REGEX, 1, 'Tier')[0]),
            exec_count=int(comp_thresholds[0]),
            threshold=int(comp_thresholds[1]),
            priority=None,
            rate=None,
            queue_size=int(queue_stats[0]),
            queue_change=int(queue_stats[1]),
            queue_load=float(queue_stats[2]),
            queue_time=int(queue_stats[3]),
            comp_time=None,
            ast_size=None,
            inline=None,
            ir=None,
            code_size_in_bytes=None,
            code_addr=None,
            comp_id=None,
            timestamp=self.parse_timestamp(segments[4]),
            source=segments[5],
            reason=segments[6],
        )

    def failed(self, log_line: str, segments: list[str]) -> TruffleEngineOptLogEntry:
        identifiers = self.match(segments[0], OPT_REGEX, 4, "Operation")
        return TruffleEngineOptLogEntry(
            raw=log_line,
            log_event_type=LogEventType.Failed,
            engine_id=int(identifiers[1]),
            id=int(identifiers[2]),
            name=identifiers[3],
            tier=int(self.match(segments[1], TIER_REGEX, 1, "Tier")[0]),
            exec_count=None,
            threshold=None,
            priority=None,
            rate=None,
            queue_size=None,
            queue_change=None,
            queue_load=None,
            queue_time=None,
            comp_time=int(self.match(segments[2], TIME_REGEX, 1, 'CompTime')[0]),
            ast_size=None,
            inline=None,
            ir=None,
            code_size_in_bytes=None,
            code_addr=None,
            comp_id=None,
            timestamp=self.parse_timestamp(segments[4]),
            source=segments[5],
            reason=segments[3],
        )


