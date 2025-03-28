from dataclasses import dataclass, field

from truffle_logs_analyzer.HotSpotLogEntry import HotSpotLogEntry
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
    evictions: list[HotSpotLogEntry] = field(default_factory=list[HotSpotLogEntry])
    enqueues: list[TruffleEngineOptLogEntry] = field(default_factory=list[TruffleEngineOptLogEntry])
    dequeues: list[TruffleEngineOptLogEntry] = field(default_factory=list[TruffleEngineOptLogEntry])

    def exec_count(self) -> int:
        if len(self.enqueues) > 0:
            return sorted(self.enqueues, key=lambda e: e.timestamp, reverse=True)[0].exec_count
        else:
            return 0

    def all_events_sorted(self) -> list:
        all_events = self.deopts
        all_events.extend(self.dones)
        all_events.extend(self.starts)
        all_events.extend(self.invals)
        all_events.extend(self.ttis)
        all_events.extend(self.failures)
        all_events.extend(self.evictions) #TODO! make hotspot evictions
        all_events.extend(self.enqueues)
        all_events.extend(self.dequeues)
        return sorted(all_events, key=lambda e: e.timestamp)
