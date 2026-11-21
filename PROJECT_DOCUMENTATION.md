# AI-KOS Developer Manual

## Overview

AI-KOS is a modular knowledge ingestion, indexing, and conversational knowledge platform built on Python. It combines legacy dataset import support with a newer KnowledgePipeline architecture to process raw files, normalize schema, store metadata, and power a search-based answer engine.

This document is the official developer manual for AI-KOS. It explains the code organization, architecture, key components, data flow, extensibility model, runtime behavior, and developer workflows.

---

## Architecture Summary

AI-KOS is structured around these core subsystems:

- `src/core/config_manager.py`: centralized configuration and filesystem path setup.
- `src/core/dataset_manager.py`: discovers datasets, loads records, caches results, and manages dataset registry.
- `src/core/dataset_loader.py`: loads CSV and JSON datasets using schema mapping and legacy handlers.
- `src/core/knowledge_factory.py`: ingest arbitrary files into the dataset store with either the new pipeline or legacy format handlers.
- `src/core/knowledge_pipeline/`: new extensible pipeline for file extraction, cleaning, normalization, topic detection, structuring, and metadata enrichment.
- `src/core/knowledge_graph.py`: lightweight concept graph that stores nodes, relations, and supports concept expansion.
- `src/core/knowledge_index.py`: search index abstraction that queries dataset indexes and metadata.
- `src/core/search_engine.py`: application-level search API used by the conversation engine.
- `src/core/brain.py`: high-level coordinator that routes queries, builds plans, executes searches, and stores memory.
- `src/core/ai_platform.py`: platform bootstrap, module discovery, dataset watcher startup, and high-level application services.

AI-KOS also includes utility systems for logging, memory, schema mapping, validation, versioning, plugin management, and diagnostics.

---

## Codebase Layout

### Top-level

- `main.py`: legacy entrypoint for the application front-end, voice mode, chat mode, and spam detection features.
- `config.py`: application-specific configuration helpers and verification functions.
- `requirements.txt`: Python dependency list.
- `datasets/`: dataset storage directory.
- `cache/`: runtime cache for metadata, dataset indexes, model artifacts, and memory.
- `logs/`: runtime logs.

### Core package

The `src/core/` package contains the AI platform implementation.

Key files and packages:

- `src/core/__init__.py`: core package exports and compatibility imports.
- `src/core/config_manager.py`: config object and `ConfigManager` helper with default paths.
- `src/core/logger.py`: rotating file logger and console logger wrapper.
- `src/core/dataset_manager.py`: dataset discovery and loading orchestration.
- `src/core/dataset_loader.py`: dataset parsing with schema mapping fallback.
- `src/core/metadata_store.py`: JSON-backed metadata persistence.
- `src/core/knowledge_graph.py`: graph storage and related entity expansion.
- `src/core/knowledge_index.py`: dataset search abstraction.
- `src/core/search_engine.py`: search interface that uses the knowledge index.
- `src/core/brain.py`: query planning and response orchestration.
- `src/core/ai_platform.py`: platform initialization and runtime service wiring.
- `src/core/knowledge_factory.py`: file import orchestration.
- `src/core/knowledge_pipeline/`: new pipeline package with extractors, stages, and registry.
- `src/core/format_handlers/`: legacy format adapter registry for backward compatibility.
- `src/core/plugin_manager.py` and `src/core/module_registry.py`: plugin discovery and module registration.
- `src/core/memory_store.py`: persistent conversational memory, schema approvals, feedback, and corrections.
- `src/core/schema_mapper.py`: header normalization, alias mapping, and row transformation.
- `src/core/validator.py`: text validation and normalization utilities.
- `src/core/version_manager.py`: dataset version tracking and rollback metadata.

### Tests

The `tests/` folder contains unit tests for pipeline workflows, format handlers, dataset health, and basic component import coverage.

- `tests/test_knowledge_pipeline.py`: validates pipeline extractor registration and TXT import.
- `tests/test_knowledge_and_imports.py`: verifies KnowledgeFactory import, format registry, knowledge graph, and dataset health.

---

## Data Flow

### Ingestion and Import

AI-KOS accepts raw source files through `KnowledgeFactory.process(path, subject)`.

1. The file is validated and normalized as a `Path`.
2. If the new `KnowledgePipeline` supports the file extension, `KnowledgePipeline.process(...)` is used.
3. Otherwise, the legacy `format_handlers.registry.load(path)` path is attempted.
4. Files are written to the configured `datasets_path` as CSV datasets.
5. After successful import, the dataset registry is refreshed so the new dataset becomes available immediately.

### KnowledgePipeline Processing

The new pipeline provides an extensible staged workflow:

1. `extractor_registry.get(path)`: selects an extractor by file extension.
2. `extractor.validate(path)`: validates the file source.
3. `extractor.extract(path)`: returns raw rows plus optional metadata.
4. `CleaningStage.process(rows)`: removes duplicates and empty rows.
5. `NormalizationStage.process(rows)`: canonicalizes field names and text values.
6. `TopicStage.detect(rows, file_name, subject)`: infers a topic and confidence score.
7. `EntityStage.extract(rows, dataset_key)`: extracts basic capitalized tokens as entities and adds them to the knowledge graph.
8. `StructuringStage.structure(rows, source, topic, confidence)`: converts each row into structured search-oriented records.
9. `MetadataStage.create(...)`: creates metadata describing file source, import status, record count, entities, and topics.
10. The CSV dataset is written, metadata is saved, the dataset manager is refreshed, and the dataset is indexed.

### Dataset Loading and Search

- `DatasetManager.discover_datasets()` scans `datasets_path` recursively for supported files and registers them.
- `DatasetManager.load_dataset(name)` uses `DatasetLoader.load(path)` to parse the file, map headers, validate rows, and create an in-memory cache.
- `KnowledgeIndex.search(query, subjects)` queries indexed dataset rows and returns results with metadata.
- `SearchEngine.search(query, subjects)` is the public search facade used by the platform.
- `Brain.execute(plan)` uses the route from `IntentRouter` and search results to build the final response.

---

## Key Components

### ConfigManager

- `ConfigManager.get(key, default)` retrieves configuration values.
- `ConfigManager.ensure_paths()` ensures all runtime directories exist and initializes feedback storage.

### DatasetManager

- Maintains run-time dataset registry, dataset cache, and indexer.
- Derives subject namespaces from directory layout under `datasets/`.
- Supports refreshing the registry when new datasets are added.

### SchemaMapper

- Normalizes raw headers using `normalize_header()`.
- Maps headers to standard canonical fields such as `title`, `description`, `category`, `label`, and `value`.
- Stores approved mappings in `MemoryStore` and reuses them when the same header shape returns.
- Maps rows to a normalized schema with a `metadata` bucket for unmapped fields.

### KnowledgeFactory

- Acts as the import facade for raw files.
- Uses the new pipeline when an extractor exists for the extension.
- Falls back to legacy format handlers for legacy dataset formats.
- Writes normalized CSV output into `datasets/` and refreshes discovery.

### KnowledgePipeline

- Orchestrates connector-specific extraction and staging logic.
- Defines extraction stages for cleaning, normalization, entity detection, topic detection, structuring, and metadata.
- Rebuilds the search and index state after every import.
- Supports plugin-friendly extension via extractor registration.

### Extractor Registry and Extractors

- `src/core/knowledge_pipeline/extractor_registry.py` provides `registry.register(ext, extractor)` and `registry.get(path)`.
- Built-in extractors currently include:
  - `csv_extractor.py`
  - `json_extractor.py`
  - `txt_extractor.py`
  - `md_extractor.py`
  - `html_extractor.py`
  - `sqlite_extractor.py`
  - `pdf_extractor.py`
  - `docx_extractor.py`
- PDF and DOCX extractor support is optional and falls back cleanly when required dependencies are missing.

### Legacy Format Handlers

- `src/core/format_handlers/__init__.py` registers legacy handlers for `csv`, `json`, `txt`, `md`, `html`, and `sqlite`.
- Format handlers preserve backwards-compatible import behavior for dataset discovery and loading.

### Memory and Feedback

- `src/core/memory_store.py` persists:
  - preferences
  - conversation summaries
  - approved schema mappings
  - corrections
  - user feedback
- Memory is stored as a JSON file under the cache path.

### Knowledge Graph

- `KnowledgeGraph` stores simple nodes and directed edges.
- `find_related(concept)` returns related nodes and edges.
- `expand_concepts(seed_concepts, depth)` returns an expanded list of related concepts.

### VersionManager

- Tracks dataset import versions.
- Records version state with source hash and validation details.
- Supports restoring and listing historical versions.

### AIPlatform

- Bootstraps the platform with configuration, dataset manager, module registry, plugin manager, metadata store, model manager, knowledge graph, and search engine.
- Starts a background `DatasetWatcher` to monitor dataset changes.
- Discovers subject modules and registers them as generic modules.

### Brain

- Coordinates query planning, execution, and response localization.
- Routes query to subject modules, executes search, expands graph concepts, and assembles final response metadata.
- Stores conversation summaries and handles low-confidence responses with learning queue tracking.

---

## Extensibility

### Adding a File Extractor

1. Add a new extractor class under `src/core/knowledge_pipeline/extractors/`.
2. Inherit `BaseExtractor` and implement `validate()`, `extract()`, and `metadata()`.
3. Register the extractor at the bottom of the extractor module:
   ```python
   registry.register('your_ext', YourExtractor())
   ```
4. The pipeline automatically uses the new extractor for matching file extensions.

### Adding a Legacy Format Handler

1. Add a new handler under `src/core/format_handlers/`.
2. Implement a `load(path)` method returning `(rows, header_map, status)`.
3. Register the handler in `src/core/format_handlers/__init__.py`.

### Adding Plugins and Modules

- `PluginManager.discover_plugins(plugin_dir)` scans directories under `plugins/`.
- Plugin modules can be registered with `ModuleRegistry`.
- `AIPlatform.discover_modules()` creates a `GenericSubjectModule` for each dataset subject.

### Schema Approval Workflow

- `SchemaMapper` can reuse approved mappings from `MemoryStore`.
- `MemoryStore.approve_schema_mapping(dataset_name, mapping)` persists user-approved mapping rules.
- Approved mappings are applied automatically when a dataset with the same normalized header shape is imported later.

---

## Runtime Behavior

### Startup Sequence

1. `ConfigManager.ensure_paths()` prepares required directories.
2. `AIPlatform` initializes core services and dataset discovery.
3. `DatasetWatcher` starts in the background.
4. `AIPlatform.discover_modules()` registers subject modules.
5. The system is ready to accept search requests and file imports.

### Dataset Watcher

- `DatasetWatcher` monitors the datasets folder and refreshes the dataset registry when changes occur.
- This ensures new files are automatically discovered without explicit restarts.

### Search and Response Flow

1. User query enters through `Brain.answer(query)`.
2. `Brain.plan(query)` routes the query with `IntentRouter`.
3. `AIPlatform.search(query, subjects)` searches dataset indexes.
4. `KnowledgeGraph.expand_concepts([query])` finds related concepts for enhanced response context.
5. `ConversationEngine.build_response(...)` composes the final answer and metadata.
6. `Brain` persists interaction summaries and learning candidates.

---

## Deployment and Development

### Local Setup

1. Ensure Python 3.12+ is installed.
2. Install dependencies from `requirements.txt`.
3. Run the application through `main.py` or import `src/core` modules in custom workflows.

### Testing

- Run `pytest` from repository root.
- The current test suite exercises knowledge import, extractor registration, legacy handler discovery, knowledge graph behavior, and dataset health.

### Important Paths

- `datasets/`: primary data store for CSV datasets.
- `cache/`: runtime cache storage for metadata, version data, and memory.
- `logs/`: rotating logs created by `src/core/logger.py`.

---

## Developer Notes

### Backward Compatibility

AI-KOS preserves earlier dataset ingestion behavior by supporting the legacy `format_handlers` pipeline. New file import flows prefer the `KnowledgePipeline` when a matching extractor is available.

### Metadata and Search

- Metadata for imported datasets is stored in `cache/metadata/<subject>/<dataset>.meta.json`.
- Dataset search indexes are created under `cache/datasets/<dataset>.idx.json`.
- `KnowledgeIndex` leverages this index and metadata to score results and return structured search items.

### Best Practices

- Keep datasets organized by subject under `datasets/<subject>/`.
- Prefer structured imports through `KnowledgeFactory` for new file types.
- Add tests for any new extractor or dataset handler.
- Use the schema approval workflow for nonstandard header names.

---

## Troubleshooting

- If a dataset is not discovered, verify the file extension is in `Config.supported_dataset_extensions`.
- If an import fails with `unsupported_format`, add an extractor or legacy handler for the extension.
- If schema mapping fails, inspect the header names and add an approved mapping via `MemoryStore` or update `SchemaMapper` aliases.
- If metadata does not appear, confirm `cache/metadata` is writable and that `KnowledgePipeline` saved metadata after ingest.

---

## Glossary

- `Subject`: derived from dataset folder hierarchy and used to group datasets by domain.
- `Dataset`: a CSV file discovered under `datasets/` that the platform can load and search.
- `Extractor`: a file-type adapter in `knowledge_pipeline/extractors/` that converts source files into structured rows.
- `Format Handler`: legacy adapter for dataset file formats used by `DatasetLoader`.
- `KnowledgeGraph`: concept relationship store used for query expansion.
- `MemoryStore`: persistent storage for conversation summaries, approvals, corrections, and feedback.
- `SchemaMapper`: normalizes headers and maps raw rows to canonical fields.

---

## Contact Points for Developers

- `src/core/knowledge_factory.py`: import facade for new and legacy ingestion.
- `src/core/knowledge_pipeline/pipeline.py`: pipeline orchestration and staging.
- `src/core/format_handlers/__init__.py`: legacy format registration.
- `src/core/knowledge_pipeline/extractor_registry.py`: extractor selection logic.
- `src/core/schema_mapper.py`: header mapping and schema normalization.
- `src/core/brain.py`: top-level query planner and executor.
- `src/core/ai_platform.py`: bootstrap and module discovery.

---

## Change Log

This document should be updated with every significant architecture change, especially when new pipeline stages, extractors, or module plugins are introduced.

---

## Appendix: Example Import Flow

```python
from src.core.config_manager import ConfigManager
from src.core.knowledge_factory import KnowledgeFactory

config = ConfigManager()
factory = KnowledgeFactory(config)
ok, status = factory.process(Path('path/to/input.txt'), subject='knowledge')
print(ok, status)
```

### Example Search Flow

```python
from src.core.brain import Brain

brain = Brain()
result = brain.answer('What is contained in the knowledge base?')
print(result)
```
