from LogEventType import LogEventType
from TruffleEngineOptLogEntry import TruffleEngineOptLogEntry


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
        elif logLine.startswith("[engine] opt failed"):
            logLine = logLine.replace("[engine] opt failed", "").strip()
            self._entry = self.parseFailedEntry(logLine);

    def entry(self):
        return self._entry

    def parseStartEntry(self, logLine):
        parts = logLine.split('|')

        if len(parts) != 7 :
            if False:
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
            if False:
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
            if False:
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
            if False:
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
            if False:
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

    def parseFailedEntry(self, logLine):
        parts = logLine.split('|')

        if len(parts) != 6 :
            if False:
                print(f"Can't parse this line that has {len(parts)} parts: {logLine}")
            return None

        targetId, engineId, callTargetName = self.parseIdComponent(parts[0])

        return TruffleEngineOptLogEntry(logLine,
                                        LogEventType.Failed,
                                        engineId,
                                        targetId,
                                        callTargetName,
                                        parts[1], # tier
                                        self.parseTimeComponent(parts[2]),     # compilation_time
                                        None,     # ast_size
                                        None,     # inlining info
                                        None,     # ir info
                                           0,     # code size info
                                        None,     # code addr info
                                        None,     # compilation id
                                        self.parseLabelAndValue(parts[4]),  # timestamp
                                        parts[5],                           # source
                                        parts[3])                           # reason


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