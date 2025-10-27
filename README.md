# Truffle Logs Analyzer

A Python utility for parsing and analyzing GraalVM Truffle engine optimization logs. This tool helps developers understand compilation behavior, performance characteristics, and optimization patterns in GraalVM Truffle-based applications.

## Overview

The Truffle Logs Analyzer processes GraalVM Truffle engine logs to extract compilation statistics, identify performance bottlenecks, and provide insights into the optimization behavior of your application. It supports both batch analysis and interactive exploration of log data.

## Features

- **Comprehensive Log Parsing**: Parses both Truffle engine optimization logs and HotSpot code cache events
- **Statistical Analysis**: Provides detailed compilation statistics including:
  - Number of compilations, invalidations, deoptimizations, and failures
  - Compilation time analysis with percentile distributions
  - Code size metrics for different compilation tiers
  - Cache thrashing detection
- **Interactive REPL Mode**: Explore log data interactively with various commands
- **Multiple Analysis Views**:
  - **Stats**: Overall compilation statistics
  - **Histogram**: Top compilation targets by compilation count
  - **Hotspots**: Most frequently executed methods
  - **Compilation Rate**: Time-based compilation activity analysis
  - **Pareto Analysis**: Distribution of compilation frequency
  - **Call Target Details**: Detailed event timeline for specific targets

## Installation

### Requirements
- Python >= 3.9
- pandas >= 2.2.3

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/JohnTortugo/truffle-logs-analyzer.git
   cd truffle-logs-analyzer
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .env
   source .env/bin/activate
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

4. Alternatively, use the provided setup script:
   ```bash
   ./truffle-logs.sh
   ```

## Usage

### Command Line Interface

```bash
truffle-logs <logfile> [options]
```

#### Options

- `--interactive`: Enter interactive REPL mode for exploring log data
- `--stats`: Print general compilation statistics
- `--histogram N`: Show top N compilation targets with most compilations
- `--hotspots N`: Show top N most frequently executed methods
- `--call_id ID`: Show detailed event timeline for specific call target ID
- `--comp_rate <hour|minute>`: Show compilation activity over time with specified granularity
- `--comp_pareto`: Show Pareto chart of compilation frequency distribution
- `--verbose`: Enable verbose output
- `--trace`: Enable detailed tracing (implies --verbose)

#### Examples

```bash
# Basic statistics
truffle-logs app.log --stats

# Interactive exploration
truffle-logs app.log --interactive

# Top 20 most compiled methods
truffle-logs app.log --histogram 20

# Hourly compilation rate analysis
truffle-logs app.log --comp_rate hour

# Detailed analysis of specific call target
truffle-logs app.log --call_id 12345
```

### Interactive REPL Mode

In interactive mode, you can use the following commands:

- `stats` - Display overall compilation statistics
- `histogram <size>` - Show top N compilation targets
- `hotspots <size>` - Show top N most executed methods
- `call_id <id>` - Show detailed events for specific call target
- `comp_rate <granularity>` - Show compilation rate (hour/minute)
- `comp_pareto` - Show Pareto distribution
- `filename` - Display current log file name
- `quit` / `exit` - Exit REPL mode

## Log Format Requirements

The analyzer expects GraalVM Truffle engine logs with optimization logging enabled. To generate compatible logs, run your GraalVM application with:

```bash
java -XX:+UnlockExperimentalVMOptions \
     -XX:+EnableJVMCI \
     -XX:+UseJVMCICompiler \
     -Dgraal.TraceTruffleCompilation=true \
     -Dgraal.TraceTruffleCompilationDetails=true \
     YourApplication
```

The tool parses log entries that:
- Start with `[engine] opt` (Truffle optimization events)
- Contain `*flushing` (HotSpot code cache events)

## Architecture

### Core Components

- **`TruffleEngineOptLogEntry`**: Represents individual log events with timestamps, compilation IDs, and metadata
- **`CallTarget`**: Aggregates all events related to a specific compilation target
- **`ParseTruffleEngineOptLogEntry`**: Parses Truffle engine optimization log entries
- **`ParseHotspotLogEntry`**: Parses HotSpot code cache flushing events
- **`LogEventType`**: Enumeration of supported log event types

### Event Types

The analyzer recognizes the following event types:
- **Enqueued**: Method queued for compilation
- **Start**: Compilation started
- **Done**: Compilation completed successfully
- **Failed**: Compilation failed
- **Deoptimization**: Runtime deoptimization occurred
- **Invalidation**: Compiled code invalidated
- **CacheFlushing**: Code evicted from cache
- **TransferToInterpreter**: Execution transferred back to interpreter

### Analysis Metrics

- **Compilation Tiers**: Tracks Tier 1 (quick) and Tier 2 (optimized) compilations
- **Code Size**: Measures generated code size in bytes/KB/MB
- **Compilation Time**: Tracks time spent in compilation (milliseconds)
- **Execution Count**: Estimates method execution frequency
- **Cache Behavior**: Identifies cache thrashing and eviction patterns

## Output Interpretation

### Statistics Output

The stats command provides:
- **Call Targets**: Number of unique methods compiled
- **Compilations**: Total compilation attempts
- **Failures**: Failed compilation attempts with reasons
- **Cache Thrashing**: Methods with high eviction rates (>90% flush/done ratio)
- **Time Analysis**: Compilation time percentiles for each tier
- **Code Generation**: Amount of native code produced

### Performance Insights

- **High failure rates** may indicate complex methods or resource constraints
- **Cache thrashing** suggests memory pressure or oversized compilations
- **Long compilation times** in high percentiles indicate optimization bottlenecks
- **Frequent invalidations** may suggest unstable type profiles
