# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Class Index Analyzer** - A high-performance Java class indexing tool that builds comprehensive class and method indexes for Java codebases. This is a standalone component of the Smart Entity CRUD Analyzer system, focused specifically on building and managing class indexes.

### Core Purpose
Create a searchable index of all Java classes and methods across multiple source paths, with intelligent caching for performance optimization. The tool supports analyzing enterprise Java applications with complex multi-module structures.

## Commands

### Running the Analyzer
```bash
# Basic class index analysis
python main.py /path/to/java/src

# Multiple source paths via settings.json
python main.py /path/to/java/src --settings .vscode/settings.json

# Search for a specific class
python main.py /path/to/java/src --class EventEntity

# Search for methods by pattern
python main.py /path/to/java/src --method insert

# Force cache rebuild
python main.py /path/to/java/src --no-cache

# Enable verbose output
python main.py /path/to/java/src --verbose
```

### Installation
```bash
pip install javalang
```

## High-Level Architecture

```
main.py (Entry Point)
  ├─→ parse_arguments() - CLI argument parsing
  ├─→ build_class_index() - Orchestrates index building
  │     └─→ MultiSourceClassIndexer (class_indexer.py)
  │           ├─→ Cache validation/loading
  │           ├─→ Java file discovery
  │           ├─→ Class/method extraction
  │           └─→ Multi-key registration
  └─→ analyze_class_index() - Analysis and reporting
        ├─→ display_class_details()
        ├─→ search_methods()
        └─→ analyze_inheritance()
```

### Key Components

1. **MultiSourceClassIndexer** (`class_indexer.py`)
   - Handles multiple Java source paths
   - Manages intelligent file-based caching
   - Resolves class name collisions across modules
   - Registers classes with multiple keys for flexible lookup

2. **Data Models** (`models.py`)
   - `ClassInfo`: Class metadata including methods and imports
   - `MethodInfo`: Method signatures and locations
   - `EntityInfo`: Entity-specific information
   - `EntityAnalysisResult`: CRUD analysis results

3. **Utilities** (`utils.py`)
   - `read_file_with_encoding()`: Multi-encoding file reader
   - `load_settings_and_resolve_paths()`: VS Code settings parser
   - `extract_package_and_class_name()`: Java parser helpers
   - `extract_method_signatures()`: Method extraction

## Key Design Features

### Multi-Source Path Index Keys
Each class is registered with multiple keys for flexible lookup:
- `"ClassName"` - Basic class name
- `"ClassName@source:path"` - Source-specific version
- `"full.package.ClassName"` - Fully qualified name
- `"full.package.ClassName@source:path"` - Full name + source

### Intelligent Caching System
- **Cache file**: `multi_source_class_index_cache.json`
- **Invalidation**: Timestamp-based (compares cache vs Java files)
- **Performance**: ~60x speedup on cached runs
- **Location**: Created in current working directory

### Source Path Resolution
- Supports relative and absolute paths
- Handles VS Code `settings.json` format
- Resolves glob patterns for JAR libraries
- Validates path existence before processing

## Configuration

### VS Code settings.json
```json
{
    "files.autoGuessEncoding": true,
    "java.project.sourcePaths": [
        "src/main/java",
        "src/test/java"
    ],
    "java.project.referencedLibraries": [
        "lib/**/*.jar"
    ]
}
```

## Performance Considerations

- Cache is essential for large codebases (1000+ files)
- Use `--verbose` to monitor progress on large analyses
- Cache location affects performance (SSD recommended)
- Multiple source paths are processed in sequence

## Integration Notes

This tool is designed as a foundation component for the larger Smart Entity CRUD Analyzer system. The class index it produces is used by other analyzers to:
- Resolve method calls across files
- Track inheritance hierarchies
- Map entity usage patterns
- Identify CRUD operations