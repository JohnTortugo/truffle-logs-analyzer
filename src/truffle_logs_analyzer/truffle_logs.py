import argparse
import datetime
from collections import defaultdict
from datetime import timedelta
from functools import cmp_to_key

from .CallTarget import CallTarget
from .LogEventType import LogEventType
from .ParseHotspotLogEntry import ParseHotspotLogEntry
from .ParseTruffleEngineOptLogEntry import ParseTruffleEngineOptLogEntry
from .ReplCommand import ReplCommand
from .TruffleEngineOptLogEntry import TruffleEngineOptLogEntry


def stats(args, call_targets: dict[int, CallTarget]) -> None:
    num_call_targets = len(call_targets)
    num_compilations = sum(len(ct.dones) for ct in call_targets.values())
    num_invalidations = sum(len(ct.invals) for ct in call_targets.values())
    num_deoptimizations = sum(len(ct.deopts) for ct in call_targets.values())
    num_failures = sum(len(ct.failures) for ct in call_targets.values())
    amount_of_produced_code = sum(dn.code_size_in_bytes for ct in call_targets.values() for dn in ct.dones)
    amount_of_time_compiling = sum(dn.comp_time for ct in call_targets.values() for dn in ct.dones)

    # Count how many call targets reached the maximum compilation threshold
    ct_with_max_compilations = []
    num_max_compilation_reached = 0
    for ct in call_targets.values():
        for flr in ct.failures:
            if "Maximum compilation" in flr.reason:
                ct_with_max_compilations.append(ct)
                num_max_compilation_reached += 1

    # Count how many flush call targets thrashed
    num_max_cache_thrashing_cts = 0
    for ct in ct_with_max_compilations:
        flushes = 0

        prev = None
        for evt in ct.all_events_sorted():
            if evt.log_event_type == LogEventType.CacheFlushing:
                if prev is not None and (prev.log_event_type == LogEventType.Done or prev.log_event_type == LogEventType.CacheFlushing):
                    flushes += 1
            prev = evt

        # Due to rolling logs, it's possible we've found flushes which have no corresponding dones...avoid divide by
        # zero in those cases
        if len(ct.dones) == 0:
            if args.verbose:
                print(f"Skipping thrash calculation for target {ct.id} as no 'done' events were encountered")
            continue

        if float(flushes)/len(ct.dones) >= 0.9:
            num_max_cache_thrashing_cts += 1

    print("Number of call targets.....................................: {value}".format(value = num_call_targets))
    print("Number of compilations.....................................: {value}".format(value = num_compilations))
    print("Number of invalidations....................................: {value}".format(value = num_invalidations))
    print("Number of deoptimizations..................................: {value}".format(value = num_deoptimizations))
    print("Number of failures.........................................: {value}".format(value = num_failures))
    print("Number of call targets that reached maximum compilation....: {value} ({perc:>.2f}%)".format(value = num_max_compilation_reached, perc = (float(num_max_compilation_reached) / num_call_targets)*100))
    print("Number of failures due to cache thrashing...................: {value}".format(value = num_max_cache_thrashing_cts))
    print("Amount of produced code (MB)...............................: {value}".format(value = amount_of_produced_code / 1024 / 1024))
    print("Amount of time compiling (Sec).............................: {value}".format(value = amount_of_time_compiling / 1000))



def details_for_call_id(call_id: int, call_targets: dict[int, CallTarget]) -> None:
    if call_id not in call_targets:
        print(f"Call target with ID {call_id} not present.")
        return 

    target = call_targets[call_id]
    num_compilations = len(target.dones)
    num_invalidations = len(target.invals)
    num_deoptimizations = len(target.deopts)
    num_failures = len(target.failures)
    num_evictions = len(target.evictions)
    amount_of_produced_code = sum(dn.code_size_in_bytes for dn in target.dones)
    amount_of_time_compiling = sum(dn.comp_time for dn in target.dones)

    print("Number of compilations..........: {value}".format(value = num_compilations))
    print("Number of invalidations.........: {value}".format(value = num_invalidations))
    print("Number of deoptimizations.......: {value}".format(value = num_deoptimizations))
    print("Number of failures..............: {value}".format(value = num_failures))
    print("Number of evictions.............: {value}".format(value = num_evictions))
    print("Amount of produced code (MB)....: {value}".format(value = amount_of_produced_code / 1024 / 1024))
    print("Amount of time compiling (Sec)..: {value}".format(value = amount_of_time_compiling / 1000))
    print("Events:")

    print("\t{type:<30} | {tier:>10} | {exec_count:>10} | {comp_id:>10} | {when:>20} | {notes:>50}"
              .format(type = "EventType", 
                      tier = "Tier", 
                      exec_count = "ExecCount",
                      comp_id = "CompId",
                      when = "Timestamp",
                      notes = "Notes"))
    print("\t-------------------------------------------------------------------------------------------------------------------------------------------------------------")

    # Find the cache eviction entry for each compilation
    flushes = {}
    all_events = target.all_events_sorted()
    for evt in all_events:
        if evt.log_event_type == LogEventType.CacheFlushing:
            flushes[evt.comp_id] = evt

    prev_evt = None
    prev_enqueued = None
    for evt in all_events:
        print("\t{type:<30} | {tier:>10} | {exec_count:>10} | {comp_id:>10} | {when}"
              .format(type = evt.log_event_type,
                      tier = evt.tier,
                      exec_count = evt.exec_count if evt.log_event_type == LogEventType.Enqueued else "",
                      comp_id = evt.comp_id if (evt.log_event_type == LogEventType.Done or evt.log_event_type == LogEventType.CacheFlushing) else "",
                      when = evt.timestamp),
              end = "")

        if evt.log_event_type == LogEventType.Done:
            if int(evt.comp_id) in flushes:
                flush_evt = flushes[evt.comp_id]
                duration = flush_evt.timestamp - evt.timestamp
                print(f"| Evicted after {duration.total_seconds()}s")
            else:
                print("| ")
        elif evt.log_event_type == LogEventType.Enqueued:
            if prev_enqueued is not None:
                exec_diff = evt.exec_count - prev_enqueued.exec_count
                secs_diff = (evt.timestamp - prev_enqueued.timestamp).total_seconds()
                print("| Execution rate {exec_diff}/{secs_diff} = {rate:>.2f}/s".format(exec_diff = exec_diff, secs_diff = secs_diff, rate = float(exec_diff)/secs_diff))
            else:
                print("| ")
            prev_enqueued = evt
        else:
            print("| ")
        
        if evt.log_event_type == LogEventType.CacheFlushing and prev_evt != LogEventType.CacheFlushing:
            print("")
        
        # Keep reference to previous
        prev_evt = evt

    print("Notes: ")
    print("       - The execution rate is computed based Truffle enqueue events. The actual execution rate might be higher.")
    



def histogram(hsize: int, call_targets: dict[int, CallTarget]) -> None:
    def compare(entry1: CallTarget, entry2: CallTarget):
        if len(entry2.dones) != len(entry1.dones):
            return len(entry2.dones) - len(entry1.dones)
        else:
            total_compile_time_1 = sum(dn.comp_time for dn in entry1.dones)
            total_compile_time_2 = sum(dn.comp_time for dn in entry2.dones)
            return total_compile_time_2 - total_compile_time_1

    values = list(call_targets.values())
    sorted_values = sorted(values, key=cmp_to_key(compare))

    print("{first:>10} | "
            "{comp_time:>15} | "
            "{total_code_size:>16} | "
            "{invals:>10} | "
            "{deopts:>10} | "
            "{evictions:>10} | "
            "{failures:>10} | "
            "{ttis:>10} | "
            "{exec_count:>10} | "
            "{second:>10} | "
            "{third:>50} | "
            "{fourth:>50}"
            .format(first = "Comps", 
                comp_time = "TotCompTime(ms)", 
                total_code_size = "TotCodeSize (KB)", 
                invals = "Invals", 
                deopts = "Deopts", 
                evictions = "evictions", 
                failures = "failures",
                ttis = "TransToInt", 
                exec_count = "ExecCount", 
                second = "ID", 
                third = "Method", 
                fourth = "Source"))
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

    for target in sorted_values[:hsize]:
        amount_of_produced_code = sum(dn.code_size_in_bytes for dn in target.dones) / 1024
        amount_of_time_compiling = sum(dn.comp_time for dn in target.dones)

        print(f"{len(target.dones):>10} | "
              f"{amount_of_time_compiling:>15} | "
              f"{amount_of_produced_code:>16.0f} | "
              f"{len(target.invals):>10} | "
              f"{len(target.deopts):>10} | "
              f"{len(target.evictions):>10} | "
              f"{len(target.failures):>10} | "
              f"{len(target.ttis):>10} | "
              f"{target.exec_count():>10} | "
              f"{target.id:>10} | "
              f"{target.name:>50} | "
              f"{target.source:>50}")


def comp_rate(granularity: str, call_targets: dict[int, CallTarget]) -> None:
    compilations = defaultdict(int)
    produced_code = defaultdict(int)
    time_spent = defaultdict(int)
    evictions = defaultdict(int)
    targets = defaultdict(set)
    cumulative_targets = set() 
    sources = defaultdict(set)
    min_time = datetime.datetime.now(datetime.timezone.utc) + timedelta(days=3650)
    max_time = datetime.datetime.now(datetime.timezone.utc) - timedelta(days=3650)

    if granularity == "hour":
        time_key_pattern = "%Y-%m-%d %H"
        minutes_increment = 60
    elif granularity == "minute":
        time_key_pattern = "%Y-%m-%d %H:%M"
        minutes_increment = 1
    else:
        print(f"Unknown comp_rate granularity '{granularity}'.")
        return

    for ct in call_targets.values():
        for dn in ct.dones:
            if dn.timestamp < min_time:
                min_time = dn.timestamp
            if dn.timestamp > max_time:
                max_time = dn.timestamp

            time_key = dn.timestamp.strftime(time_key_pattern)
            compilations[time_key] += 1
            produced_code[time_key] += dn.code_size_in_bytes
            time_spent[time_key] += dn.comp_time
            sources[time_key].add(ct.source)
            targets[time_key].add(ct.id)

        for eviction in ct.evictions:
            time_key = eviction.timestamp.strftime(time_key_pattern)
            evictions[time_key] += 1

    print("{time_key:>20} | {compilations:>15} | {code:>15} | {time:>15} | {targets:>15} | {sources:>15} | {cumul_tgts:>15} | {sum_uniq_comps:>15} | {evictions:>15} |"
            .format(time_key = "Datetime", compilations = "Compilations", code = "CodeGen (MB)", time = "CmplTime (s)", targets = "CallTargets", sources = "Sources", cumul_tgts = "CumTargets", sum_uniq_comps = "SumUniqComps (MB)", evictions = "Evictions"))

    curr_time = min_time
    while curr_time <= max_time:
        time_key = curr_time.strftime(time_key_pattern)

        # Find which is the largest compilation done within the given "time_key"
        sum_largest_compilations = 0
        for ct_id in targets[time_key]:
            cumulative_targets.add(ct_id)
            ct = call_targets[ct_id]
            mx = 0
            for dn in ct.dones:
                dn_time = dn.timestamp.strftime(time_key_pattern)
                if dn_time == time_key:
                    if mx < dn.code_size_in_bytes:
                        mx = dn.code_size_in_bytes
            sum_largest_compilations += mx

        print(f"{time_key:>20} | "
              f"{compilations[time_key]:>15} | "
              f"{produced_code[time_key]/1024/1024:>15.0f} | "
              f"{time_spent[time_key]/1000:>15.3f} | "
              f"{len(targets[time_key]):>15} | "
              f"{len(sources[time_key]):>15} | " 
              f"{len(cumulative_targets):>15} | " 
              f"{sum_largest_compilations/1024/1024:>15.0f} | " 
              f"{evictions[time_key]:>15} | ")

        curr_time = curr_time + timedelta(minutes=minutes_increment)



def comp_pareto(call_targets: dict[id, CallTarget]):
    counts = [0] * 101
    for ct in call_targets.values():
        counts[len(ct.dones)] += 1

    print("{freq:>5} | {count:>7} | {curr_perc:>7} | {acc_perc:>7}".format(freq = "Freq", count = "Count", curr_perc = "Curr%", acc_perc = "Acc%"))
    print("---------------------------")
    acc_perc = 0
    for freq in range(1, 101):
        curr_perc = float(counts[freq])/len(call_targets)
        acc_perc += curr_perc
        print("{freq:>5} | {count:>5} | {curr_perc:>7.2f}% | {acc_perc:>7.2f}%".format(freq = freq, count = counts[freq], curr_perc = curr_perc*100, acc_perc = acc_perc*100))


def hotspots(hsize: int, call_targets: dict[id, CallTarget]):
    def compare(entry1: CallTarget, entry2: CallTarget):
        if entry2.exec_count() != entry1.exec_count():
            return entry2.exec_count() - entry1.exec_count()
        else:
            return len(entry1.dones) - len(entry2.dones)

    values = list(call_targets.values())
    targets = sorted(values, key=cmp_to_key(compare))

    print("{first:>10} | "
            "{comp_time:>15} | "
            "{total_code_size:>16} | "
            "{invals:>10} | "
            "{deopts:>10} | "
            "{evictions:>10} | "
            "{failures:>10} | "
            "{ttis:>10} | "
            "{exec_count:>10} | "
            "{second:>10} | "
            "{third:>50} | "
            "{fourth:>50}"
            .format(first = "Comps", 
                comp_time = "TotCompTime(ms)", 
                total_code_size = "TotCodeSize (KB)", 
                invals = "Invals", 
                deopts = "Deopts", 
                evictions = "evictions", 
                failures = "failures", 
                ttis = "TransToInt", 
                exec_count = "ExecCount", 
                second = "ID", 
                third = "Method", 
                fourth = "Source"))
    print("--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

    for i in range(0, hsize):
        target = targets[i]
        amount_of_produced_code = sum(dn.code_size_in_bytes for dn in target.dones) / 1024
        amount_of_time_compiling = sum(dn.comp_time for dn in target.dones)

        print(f"{len(target.dones):>10} | "
              f"{amount_of_time_compiling:>15} | "
              f"{amount_of_produced_code:>16.0f} | "
              f"{len(target.invals):>10} | "
              f"{len(target.deopts):>10} | "
              f"{len(target.evictions):>10} | "
              f"{len(target.failures):>10} | "
              f"{len(target.ttis):>10} | "
              f"{target.exec_count():>10} | "
              f"{target.id:>10} | "
              f"{target.name:>50} | "
              f"{target.source:>50}")


def parse_log_file(args) -> tuple[list[TruffleEngineOptLogEntry], list[TruffleEngineOptLogEntry]]:
    hotspot_events: list[TruffleEngineOptLogEntry] = []
    truffle_events: list[TruffleEngineOptLogEntry] = []

    with open(args.logfile, 'r') as file:
        for line in file:
            stripped = line.rstrip()
            if stripped.startswith("[engine] opt"):
                entry = ParseTruffleEngineOptLogEntry(stripped).entry()
                if entry is not None:
                    truffle_events.append(entry)
                elif args.trace:
                    print(f"Ignoring engine log entry: {stripped}")
            elif stripped.find("*flushing ") >= 0:
                entry = ParseHotspotLogEntry(stripped).entry()
                if entry is not None:
                    hotspot_events.append(entry)
                elif args.trace:
                    print(f"Ignoring codecache log entry: {stripped}")
            elif args.trace:
                print(f"Ignoring log entry: {stripped}")

    return hotspot_events, truffle_events


def collect_call_targets(events: list[TruffleEngineOptLogEntry]) -> dict[int, CallTarget]:
    call_targets: dict[int, CallTarget] = {}

    for event in events:
        if event.id not in call_targets:
            call_targets[event.id] = CallTarget(id=event.id, name=event.name, source=event.source)

    return call_targets


def populate_events_to_call_targets(
        call_targets: dict[int, CallTarget],
        hotspot_events: list[TruffleEngineOptLogEntry],
        truffle_events: list[TruffleEngineOptLogEntry]) -> None:

    # TODO -> I don't think call target names are necessarily unique so this seems like different targets
    #         may collide on the same name
    speedup: dict[str, CallTarget] = {}
    for ct in call_targets.values():
        speedup[ct.name] = ct

    for truffle_event in truffle_events:
        if truffle_event.log_event_type == LogEventType.Start :
            call_targets[truffle_event.id].starts.append(truffle_event)

        elif truffle_event.log_event_type == LogEventType.Enqueued :
            call_targets[truffle_event.id].enqueues.append(truffle_event)

        elif truffle_event.log_event_type == LogEventType.Dequeued:
            call_targets[truffle_event.id].dequeues.append(truffle_event)

        elif truffle_event.log_event_type == LogEventType.Done :
            call_targets[truffle_event.id].dones.append(truffle_event)

        elif truffle_event.log_event_type == LogEventType.Deoptimization :
            call_targets[truffle_event.id].deopts.append(truffle_event)

        elif truffle_event.log_event_type == LogEventType.Invalidation :
            call_targets[truffle_event.id].invals.append(truffle_event)

        elif truffle_event.log_event_type == LogEventType.Failed:
            call_targets[truffle_event.id].failures.append(truffle_event)

        elif truffle_event.log_event_type == LogEventType.TransferToInterpreter:
            if truffle_event.name in speedup:
                target = speedup[truffle_event.name]
                call_targets[target.id].ttis.append(truffle_event)

    truffle_id_to_hotspot_id: dict[int, int]= {}
    for ct in call_targets.values():
        for done in ct.dones:
            truffle_id_to_hotspot_id[done.comp_id] = ct.id

    for hotspot_event in hotspot_events:
        if hotspot_event.comp_id in truffle_id_to_hotspot_id:
            call_targets[truffle_id_to_hotspot_id[hotspot_event.comp_id]].evictions.append(hotspot_event)


def repl_prompt():
    while True:
        print("truffle ::> ", end="")
        line = input().strip()
        if line == "" or len(line.split()) == 0:
            continue 
        
        parts = line.strip().split()
        cmd = parts[0].strip()
        if cmd == "quit" or cmd == "exit":
            return ReplCommand.Quit, None
        elif cmd == "stats":
            return ReplCommand.Stats, None
        elif cmd == "histogram":
            if len(parts) > 1:
                return ReplCommand.Histogram, [int(parts[1])]
            else:
                print("Missing histogram size argument.")
        elif cmd == "call_id":
            if len(parts) > 1:
                return ReplCommand.CallId, [int(parts[1])]
            else:
                print("Missing call target id argument.")
        elif cmd == "hotspots":
            if len(parts) > 1:
                return ReplCommand.Hotspots, [int(parts[1])]
            else:
                print("Missing number of methods to list.")
        elif cmd == "comp_rate":
            if len(parts) > 1:
                return ReplCommand.CompRate, [parts[1]]
            else:
                print("Missing granularity to list comp_rate.")
        elif cmd == "comp_pareto":
            return ReplCommand.CompPareto, None
        elif cmd == "filename":
            return ReplCommand.FileName, None
        else:
            print(f"What's '{cmd}' ?!?")



def repl(args,
         call_targets: dict[int, CallTarget],
         hotspot_events: list[TruffleEngineOptLogEntry],
         truffle_events: list[TruffleEngineOptLogEntry]) -> None:
    while True:
        cmd, info = repl_prompt()
        if cmd == ReplCommand.Quit:
            return
        elif cmd == ReplCommand.Stats:
            stats(args, call_targets)
        elif cmd == ReplCommand.Histogram:
            histogram(info[0], call_targets)
        elif cmd == ReplCommand.CallId:
            details_for_call_id(info[0], call_targets)
        elif cmd == ReplCommand.Hotspots:
            hotspots(info[0], call_targets)
        elif cmd == ReplCommand.CompRate:
            comp_rate(info[0], call_targets)
        elif cmd == ReplCommand.FileName:
            print(args.logfile)
        elif cmd == ReplCommand.CompPareto:
            comp_pareto(call_targets)
        else:
            print("What?!")


def main():
    parser = argparse.ArgumentParser(description='GraalVM Truffle Logs Utility')
    parser.add_argument('logfile', type=str, help='Path of file containing Truffle engine logs.')
    parser.add_argument('--interactive', action='store_true', help='Enter the REPL mode.')
    parser.add_argument('--histogram', type=int, help='Print histogram with top N compilation targets with most compilations.')
    parser.add_argument('--stats', action='store_true', help='Print general information about compilations.')
    parser.add_argument('--call_id', type=int, help='Print all events related to the call target with the ID specified.')
    parser.add_argument('--comp_rate', type=str, help='Print several statistics on a <hour/minute> granularity.')
    parser.add_argument('--comp_pareto', action='store_true', help='Print pareto chart of number of call targets by number of compilations.')
    parser.add_argument('--hotspots', type=int, help='Print top N methods most executed.')
    parser.add_argument('--verbose', action='store_true', help='Print tracing messages.')
    parser.add_argument('--trace', action='store_true', help='Print detailed tracing messages.')

    args = parser.parse_args()
    if args.trace:
        args.verbose = True

    hotspot_events, truffle_events = parse_log_file(args)
    print("Parsing done.")
    call_targets = collect_call_targets(truffle_events)
    print("Collecting call targets done.")
    populate_events_to_call_targets(call_targets, hotspot_events, truffle_events)
    print("Populating call targets done.")

    if args.interactive:
        repl(args, call_targets, hotspot_events, truffle_events)
    else:
        if args.histogram is not None and args.histogram > 0 :
            histogram(args.histogram, call_targets)

        if args.call_id is not None and args.call_id > 0 :
            details_for_call_id(args.call_id, call_targets)

        if args.comp_rate is not None and args.comp_rate != "" :
            comp_rate(args.comp_rate, call_targets)

        if args.comp_pareto:
            comp_pareto(call_targets)

        if args.hotspots is not None and args.hotspots > 0:
            hotspots(args.hotspots, call_targets)

        if args.stats:
            stats(args, call_targets)

if __name__=="__main__":
    main()