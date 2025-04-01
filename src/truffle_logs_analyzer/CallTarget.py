from dataclasses import dataclass, field

from truffle_logs_analyzer.LogEventType import LogEventType
from truffle_logs_analyzer.TruffleEngineOptLogEntry import TruffleEngineOptLogEntry


@dataclass
class CallTarget:
    id: int
    name: str
    source: str
    starts: list[TruffleEngineOptLogEntry] = field(default_factory=list[TruffleEngineOptLogEntry])
    dones: list[TruffleEngineOptLogEntry] = field(default_factory=list[TruffleEngineOptLogEntry])
    deopts: list[TruffleEngineOptLogEntry] = field(default_factory=list[TruffleEngineOptLogEntry])
    invals: list[TruffleEngineOptLogEntry] = field(default_factory=list[TruffleEngineOptLogEntry])
    ttis: list[TruffleEngineOptLogEntry] = field(default_factory=list[TruffleEngineOptLogEntry])
    failures: list[TruffleEngineOptLogEntry] = field(default_factory=list[TruffleEngineOptLogEntry])
    evictions: list[TruffleEngineOptLogEntry] = field(default_factory=list[TruffleEngineOptLogEntry])
    enqueues: list[TruffleEngineOptLogEntry] = field(default_factory=list[TruffleEngineOptLogEntry])
    dequeues: list[TruffleEngineOptLogEntry] = field(default_factory=list[TruffleEngineOptLogEntry])

    def exec_count(self) -> int:
        if len(self.enqueues) > 0:
            return sorted(self.enqueues, key=lambda e: e.timestamp, reverse=True)[0].exec_count
        else:
            return 0

    def all_events_sorted(self) -> list[TruffleEngineOptLogEntry]:
        all_events = self.deopts
        all_events.extend(self.dones)
        all_events.extend(self.starts)
        all_events.extend(self.invals)
        all_events.extend(self.ttis)
        all_events.extend(self.failures)
        all_events.extend(self.evictions)
        all_events.extend(self.enqueues)
        all_events.extend(self.dequeues)

        # Sometimes Truffle emits events with the exact same timestamp (perhaps it's not granular enough?)
        # In that case, we'll assume queued, start, and done events follow in that order
        type_priority = { LogEventType.Enqueued: 1, LogEventType.Start: 2, LogEventType.Done: 3, }
        def sort_by_timestamp_and_type(event: TruffleEngineOptLogEntry):
            # Use the priority mapping for the secondary sort
            return event.timestamp, type_priority.get(event.log_event_type, 999)

        return sorted(all_events, key=sort_by_timestamp_and_type)
