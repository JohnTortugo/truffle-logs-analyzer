#!/usr/bin/python3

import argparse
from datetime import datetime, timedelta
from functools import cmp_to_key
from enum import Enum


class CallTarget:
    def __init__(self, id, name, source):
        self._id      = id
        self._name    = name
        self._source  = source
        self._starts  = []                # Collection of entries representing log entries of type compilation start 
        self._dones   = []                # Collection of entries representing log entries of type compilation done 
        self._deopts  = []                # Collection of entries representing log entries of type deoptizations 
        self._invals  = []                # Collection of entries representing log entries of type invalidations
        self._evictions = []                # Collection of entries representing code cache evictions of this call target

    def all_events_sorted(self):
        all_events = self._deopts
        all_events.extend(self._dones)
        all_events.extend(self._starts)
        all_events.extend(self._invals)
        all_events.extend(self._evictions)
        return sorted(all_events, key=lambda e: e._timestamp)

class LogEventType(Enum):
    Start          = 1
    Done           = 2
    Deoptization   = 3
    Invalidation   = 4
    Unqueue        = 5
    CacheFlushing  = 6
    Failed         = 7


class TruffleEngineOptLogEntry:
    def __init__(self, raw, logEventType, engineId, id, name, tier, comp_time, ast_size, inline, ir, code_size_in_bytes, code_addr, comp_id, timestamp, source, reason):
        self._raw       = raw
        self._eventType = logEventType
        self._engineId  = engineId
        self._id        = id
        self._name      = name
        self._tier      = tier
        self._comp_time = int(comp_time)
        self._ast_size  = ast_size
        self._inline    = inline
        self._ir        = ir
        self._code_size_in_bytes = int(code_size_in_bytes)
        self._code_addr = code_addr
        self._comp_id   = comp_id
        self._timestamp = datetime.strptime(timestamp+"+0000", "%Y-%m-%dT%H:%M:%S.%f%z") # "+0000" to keep all datetimes in same format
        self._source    = source
        self._reason    = reason

    def __str__(self):
        return f"{self._eventType} | {self._raw}"


class HotSpotLogEntry:
    def __init__(self, raw, logEventType, hotspotCompId, timestamp):
        self._raw       = raw
        self._tier      = "" 
        self._eventType = logEventType
        self._hotspotCompId  = hotspotCompId
        self._timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")

    def __str__(self):
        return f"{self._eventType} | {self._raw}"




class ParseTruffleEngineLogEntry:
    def __init__(self, logLine):
        self._entry = None
        logLine = logLine.strip()
        
        if logLine.startswith("[engine] opt done"):
            logLine = logLine.replace("[engine] opt done", "").strip()
            self._entry = self.parseDoneEntry(logLine);
        elif logLine.startswith("[engine] opt inval"): 
            logLine = logLine.replace("[engine] opt inval.", "").strip()
            self._entry = self.parseInvalEntry(logLine);
        elif logLine.startswith("[engine] opt deopt"): 
            logLine = logLine.replace("[engine] opt deopt", "").strip()
            self._entry = self.parseDeoptEntry(logLine);
        elif logLine.startswith("[engine] opt start"): 
            logLine = logLine.replace("[engine] opt start", "").strip()
            self._entry = self.parseStartEntry(logLine);
        elif logLine.startswith("[engine] opt unque"): 
            logLine = logLine.replace("[engine] opt unque", "").strip()
            self._entry = self.parseUnqueueEntry(logLine);
        
    def entry(self):
        return self._entry

    def parseStartEntry(self, logLine):
        parts = logLine.split('|')

        if len(parts) != 7 : 
            if args.trace:
                print(f"Can't parse this line that has {len(parts)} parts: {logLine}")
            return None

        targetId, engineId, callTargetName = self.parseIdComponent(parts[0])

        return TruffleEngineOptLogEntry(logLine,
                                        LogEventType.Start,
                                        engineId,
                                        targetId,
                                        callTargetName,
                                        parts[1], # tier
                                           0,     # compilation_time
                                        None,     # ast_size
                                        None,     # inlining info
                                        None,     # ir info
                                           0,     # code size info
                                        None,     # code addr info
                                        None,     # compilation id
                                        self.parseLabelAndValue(parts[5]),  # timestamp
                                        parts[6],                           # source
                                        None)                               # reason

    def parseInvalEntry(self, logLine):
        parts = logLine.split('|')

        if len(parts) != 4 : 
            if args.trace:
                print(f"Can't parse this line that has {len(parts)} parts: {logLine}")
            return None

        targetId, engineId, callTargetName = self.parseIdComponent(parts[0])

        return TruffleEngineOptLogEntry(logLine,
                                        LogEventType.Invalidation,
                                        engineId,
                                        targetId,
                                        callTargetName,
                                          "", # tier
                                           0, # compilation_time
                                        None, # ast_size
                                        None, # inlining info
                                        None, # ir info
                                           0, # code size info
                                        None, # code addr info
                                        None, # compilation id
                                        self.parseLabelAndValue(parts[1]),  # timestamp
                                        parts[2],                           # source
                                        parts[3])                           # reason

    def parseDeoptEntry(self, logLine):
        parts = logLine.split('|')

        if len(parts) != 4 : 
            if args.trace:
                print(f"Can't parse this deopt entry line that has {len(parts)} parts: {logLine}")
            return None

        targetId, engineId, callTargetName = self.parseIdComponent(parts[0])

        return TruffleEngineOptLogEntry(logLine,
                                        LogEventType.Deoptization,
                                        engineId,
                                        targetId,
                                        callTargetName,
                                          "", # tier
                                           0, # compilation_time
                                        None, # ast_size
                                        None, # inlining info
                                        None, # ir info
                                           0, # code size info
                                        None, # code addr info
                                        None, # compilation id
                                        self.parseLabelAndValue(parts[2]), # timestamp
                                        parts[3],                          # source
                                        None) #reason

    def parseUnqueueEntry(self, logLine):
        parts = logLine.split('|')

        if len(parts) != 7 : 
            if args.trace:
                print(f"Can't parse this line that has {len(parts)} parts: {logLine}")
            return None

        targetId, engineId, callTargetName = self.parseIdComponent(parts[0])

        return TruffleEngineOptLogEntry(logLine,
                                        LogEventType.Start,
                                        engineId,
                                        targetId,
                                        callTargetName,
                                        parts[1], # tier
                                           0,     # compilation_time
                                        None,     # ast_size
                                        None,     # inlining info
                                        None,     # ir info
                                           0,     # code size info
                                        None,     # code addr info
                                        None,     # compilation id
                                        self.parseLabelAndValue(parts[4]),  # timestamp
                                        parts[5],                           # source
                                        parts[6])                           # reason

    def parseDoneEntry(self, logLine):
        parts = logLine.split('|')

        if len(parts) != 11 : 
            if args.trace:
                print(f"Can't parse this line that has {len(parts)} parts: {logLine}")
            return None

        targetId, engineId, callTargetName = self.parseIdComponent(parts[0])

        return TruffleEngineOptLogEntry(logLine,
                                        LogEventType.Done,
                                        engineId,
                                        targetId,
                                        callTargetName,
                                        parts[1], # tier
                                        self.parseTimeComponent(parts[2]), # compilation_time
                                        parts[3], # ast_size
                                        parts[4], # inlining info
                                        parts[5], # ir info
                                        self.parseLabelAndValue(parts[6]), # code size info
                                        self.parseLabelAndValue(parts[7]), # code addr info
                                        self.parseLabelAndValue(parts[8]), # compilation id
                                        self.parseLabelAndValue(parts[9]), # timestamp
                                        parts[10],                         # source
                                        None) # reason

    def parseLabelAndValue(self, component):
        parts = " ".join(component.split()).split(' ')
        return parts[1]

    def parseTimeComponent(self, component):
        parts = " ".join(component.split()).split('(')
        prefix = parts[0]
        parts = prefix.split(' ')
        return parts[1]

    def parseIdComponent(self, idComponent):
        parts = " ".join(idComponent.split()).split(' ')
        parts2 = parts[1].split('=')
        if len(parts) >= 2 : 
            return int(parts2[1]), -1, '-'.join(parts[2:])
        else:
            return int(parts2[1]), -1, "unknown"






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



def size_grouped(entries):
    for moment, value in entries.items():
        total_size = 0
        #print(moment)
        for id, entry in value.items():
            #print("\t", end="")
            #print(entry ,end="")
            total_size += entry._size
        print(moment + "," + str(total_size))


def compilation_rate(args, events):
    grouped_by_second = {}
    grouped_by_minute = {}
    grouped_by_hour = {}

    for event in events:
        second_key = event._timestamp.strftime("%Y-%m-%d %H:%M:%S")
        minute_key = event._timestamp.strftime("%Y-%m-%d %H:%M")
        hour_key = event._timestamp.strftime("%Y-%m-%d %H")

        if second_key not in grouped_by_second:
            grouped_by_second[second_key] = {}
        if minute_key not in grouped_by_minute:
            grouped_by_minute[minute_key] = {}
        if hour_key not in grouped_by_hour:
            grouped_by_hour[hour_key] = {}

        grouped_by_second[second_key][str(event._id)+event._tier] = event
        grouped_by_minute[minute_key][str(event._id)+event._tier] = event
        grouped_by_hour[hour_key][str(event._id)+event._tier] = event

    size_grouped(grouped_by_hour)


def stats(args, events, call_targets):
    num_call_targets = len(call_targets)
    num_compilations = sum(len(ct._dones) for ct in call_targets.values())
    num_invalidations = sum(len(ct._invals) for ct in call_targets.values())
    num_deoptimizations = sum(len(ct._deopts) for ct in call_targets.values())
    amount_of_produced_code = sum(dn._code_size_in_bytes for ct in call_targets.values() for dn in ct._dones)
    amount_of_time_compiling = sum(dn._comp_time for ct in call_targets.values() for dn in ct._dones)

    print("Number of call targets: {value}".format(value = num_call_targets))
    print("Number of compilations: {value}".format(value = num_compilations))
    print("Number of invalidations: {value}".format(value = num_invalidations))
    print("Number of deoptimizations: {value}".format(value = num_deoptimizations))
    print("Amount of produced code (Mbytes): {value}".format(value = amount_of_produced_code / 1024 / 1024))
    print("Amount of time compiling (Seconds): {value}".format(value = amount_of_time_compiling / 1000))



def details_for_call_id(args, events, call_targets):
    if args.call_id not in call_targets:
        print(f"Call target with ID {args.call_id} not present.")
        return 

    target = call_targets[int(args.call_id)]
    num_compilations = len(target._dones)
    num_invalidations = len(target._invals)
    num_deoptimizations = len(target._deopts)
    num_evictions = len(target._evictions)
    amount_of_produced_code = sum(dn._code_size_in_bytes for dn in target._dones)
    amount_of_time_compiling = sum(dn._comp_time for dn in target._dones)

    print("Number of compilations: {value}".format(value = num_compilations))
    print("Number of invalidations: {value}".format(value = num_invalidations))
    print("Number of deoptimizations: {value}".format(value = num_deoptimizations))
    print("Number of evictions: {value}".format(value = num_evictions))
    print("Amount of produced code (Mbytes): {value}".format(value = amount_of_produced_code / 1024 / 1024))
    print("Amount of time compiling (Seconds): {value}".format(value = amount_of_time_compiling / 1000))
    print("Events:")

    for evt in target.all_events_sorted():
        print(evt)
        #print("\t{type:>30} | {tier:>10} | {when}".format(type = evt._eventType, tier = evt._tier, when = evt._timestamp))




def histogram(args, events, call_targets):
    def compare(entry1, entry2):
        if len(entry2._dones) != len(entry1._dones):
            return len(entry2._dones) - len(entry1._dones)
        else:
            timec1 = sum(dn._comp_time for dn in entry1._dones)
            timec2 = sum(dn._comp_time for dn in entry2._dones)
            return timec2 - timec1

    values = list(call_targets.values())
    sortedvalues = sorted(values, key=cmp_to_key(compare))

    print("{first:>10} | {comp_time:>12} | {total_code_size:>15} | {invals:>10} | {deopts:>10} | {evictions:>10} | {second:>10} | {third:>50} | {fourth:>50}"
            .format(first = "Comps", comp_time = "TotCompTime(ms)", total_code_size = "TotCodeSize (Kb)", invals = "Invals", deopts = "Deopts", evictions = "evictions", second = "ID", third = "Method", fourth = "Source"))
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

    for target in sortedvalues[:args.histogram]:
        amount_of_produced_code = sum(dn._code_size_in_bytes for dn in target._dones) / 1024
        amount_of_time_compiling = sum(dn._comp_time for dn in target._dones)
        print(f"{len(target._dones):>10} | {amount_of_time_compiling:>12} | {amount_of_produced_code:>15.0f} | {len(target._invals):>10} | {len(target._deopts):>10} | {len(target._evictions):>10} | {target._id:>10} | {target._name:>50} | {target._source:>50}")


def parseLogFile(args):
    hotspotEvents = []
    truffleEvents = []
    lines = []

    with open(args.logfile, 'r') as file:
        for line in file:
            lines.append(line)

    for i in range(len(lines)):
        line = lines[i]
        if line.startswith("[engine] opt"): 
            entry = ParseTruffleEngineLogEntry(line).entry()
            if entry != None :
                truffleEvents.append(entry)
        elif line.find("*flushing ") >= 0:
            entry = ParseHotspotLogEntry(line).entry()
            if entry != None :
                hotspotEvents.append(entry)
            if (args.trace):
                print(f"Ignoring codecache log entry: {line}")
        elif line.find("[engine] transferToInterpreter at") >= 0:
            i += 1
            line = lines[i]
            #print(line)
            #entry = ParseTruffleEngineLogEntry(line).entry()
            #if entry != None :
            #    truffleEvents.append(entry)

    return hotspotEvents, truffleEvents


def collectCallTargets(events):
    call_targets = {}

    for event in events:
        if event._id not in call_targets:
            call_targets[int(event._id)] = CallTarget(event._id, event._name, event._source)

    return call_targets


def populateEventsToCallTargets(call_targets, hotspotEvents, truffleEvents):
    for truffleEvent in truffleEvents:
        if truffleEvent._eventType == LogEventType.Start :
            call_targets[truffleEvent._id]._starts.append(truffleEvent)
        elif truffleEvent._eventType == LogEventType.Done :
            call_targets[truffleEvent._id]._dones.append(truffleEvent)
        elif truffleEvent._eventType == LogEventType.Deoptization :
            call_targets[truffleEvent._id]._deopts.append(truffleEvent)
        elif truffleEvent._eventType == LogEventType.Invalidation :
            call_targets[truffleEvent._id]._invals.append(truffleEvent)

    speedup = {}
    for ct in call_targets.values():
        for done in ct._dones:
            speedup[int(done._comp_id)] = int(ct._id)

    for hotspotEvent in hotspotEvents:
        if int(hotspotEvent._hotspotCompId) in speedup:
            call_targets[speedup[hotspotEvent._hotspotCompId]]._evictions.append(hotspotEvent)
        #else:
        #    print(f"Didn't find {hotspotEvent._hotspotCompId} in speedup.")


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='GraalVM Truffle Logs Utility')
    parser.add_argument('logfile', type=str, help='Path of file containing Truffle engine logs.')
    parser.add_argument('--histogram', type=int, help='Print histogram with top N compilation targets with most compilations.')
    parser.add_argument('--stats', action='store_true', help='Print general information about compilations.')
    parser.add_argument('--call_id', type=int, help='Print all events related to the call target with the ID specified.')
    parser.add_argument('--verbose', action='store_true', help='Print tracing messages.')
    parser.add_argument('--trace', action='store_true', help='Print detailed tracing messages.')

    args = parser.parse_args()
    if (args.trace):
        args.verbose = True

    hotspotEvents, truffleEvents = parseLogFile(args)
    call_targets = collectCallTargets(truffleEvents)

    populateEventsToCallTargets(call_targets, hotspotEvents, truffleEvents)

    if args.histogram != None and args.histogram > 0 :
        histogram(args, truffleEvents, call_targets)

    if args.call_id != None and args.call_id > 0 :
        details_for_call_id(args, truffleEvents, call_targets)

    if args.stats :
        stats(args, truffleEvents, call_targets)

    #else:
    #    compilation_rate(args, events)

