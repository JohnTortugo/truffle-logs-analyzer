class CallTarget:
    def __init__(self, id, name, source):
        self._id      = id
        self._name    = name
        self._source  = source
        self._starts  = []                # Collection of entries representing log entries of type compilation start 
        self._dones   = []                # Collection of entries representing log entries of type compilation done 
        self._deopts  = []                # Collection of entries representing log entries of type deoptizations 
        self._invals  = []                # Collection of entries representing log entries of type invalidations
        self._ttis    = []                # Collection of entries representing log entries of type transferToInterpreter*
        self._failures  = []              # Collection of entries representing log entries of type failure
        self._evictions = []              # Collection of entries representing code cache evictions of this call target

    def all_events_sorted(self):
        all_events = self._deopts
        all_events.extend(self._dones)
        all_events.extend(self._starts)
        all_events.extend(self._invals)
        all_events.extend(self._ttis)
        all_events.extend(self._failures)
        all_events.extend(self._evictions)
        return sorted(all_events, key=lambda e: e._timestamp)