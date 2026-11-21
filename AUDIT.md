# Phase 0 Audit - AI-KOS Baseline

## Repository Snapshot

The audited baseline commit is `5801955` (`main`). The baseline contained 98 files and its tracked payload was the original AI-KOS/JARVIS repository. No file in the baseline exceeded 500 KB. Current `.git` is 207,039 bytes and the baseline working tree was approximately 510 KB.

## Full Baseline Tree

```text
.
|-- PROJECT_DOCUMENTATION.md
|-- all voices.txt
|-- automation_engine.py
|-- brain.py
|-- code_engine.py
|-- code_kb.py
|-- config.py
|-- knowledge_engine (1).py
|-- main.py
|-- memory.json
|-- memory.py
|-- memory_engine.py
|-- network_runner.py
|-- nlp_engine.py
|-- speech_engine.py
|-- tech_kb.py
|-- training_mode (1).py
|-- triggers.py
|-- tts_engine.py
|-- requirements.txt
|-- .gitignore
|-- datasets/spam_detection/.gitkeep
|-- datasets/spam_detection/user_feedback.csv
|-- memory_data/conversation.json
|-- memory_data/profile.json
|-- src/
|   |-- __init__.py
|   |-- main_spam_module.py
|   |-- core/
|   |   |-- config_manager.py
|   |   |-- logger.py
|   |   |-- validator.py
|   |   |-- memory_store.py
|   |   |-- ai_platform.py, brain.py, cache_manager.py
|   |   |-- dataset_manager.py, dataset_loader.py, dataset_health.py, dataset_watcher.py
|   |   |-- knowledge_factory.py, knowledge_graph.py, knowledge_index.py, search_engine.py
|   |   |-- format_handlers/, knowledge_pipeline/
|   |   |-- intent_router.py, conversation_engine.py, diagnostics_manager.py
|   |   |-- indexer.py, schema_mapper.py, version_manager.py
|   |   |-- plugin_manager.py, module_registry.py, metadata_store.py
|   |   |-- model_manager.py, security_manager.py, update_manager.py
|   |   |-- language_manager.py, learning_system.py, ontology.py, subject_module.py
|   |-- inference/ (spam_detector.py, spam_service.py, generic_predictor.py)
|   |-- preprocessing/spam_preprocessor.py
|   |-- training/spam_trainer.py, spam_feedback.py, generic_trainer.py
|   |-- evaluation/spam_metrics.py
|   `-- utils/
```

## Core Import Graph

| Module | Baseline purpose | Importers / dependencies |
|---|---|---|
| `config_manager.py` | Dataclass configuration and runtime path setup | `spam_detector`, `spam_service`, `spam_trainer`, core platform modules |
| `logger.py` | Rotating file and console logging | Nearly all core, training, and inference modules |
| `validator.py` | String validation and normalization | spam preprocessor/trainer/detector, pipeline, format handlers |
| `memory_store.py` | JSON-backed preferences, summaries, schema approvals, corrections, feedback | learning system, knowledge factory, Brain |
| `dataset_manager.py` | Dataset discovery and loading | Spam service, knowledge platform, diagnostics |
| `dataset_loader.py` | CSV/JSON loading and schema mapping | Dataset manager |
| `knowledge_pipeline/` | Extractor/stage pipeline | Knowledge factory; imports schema, validator, and logger |
| `knowledge_factory.py` | Raw-file ingestion | AI platform |
| `knowledge_graph.py` | Concept nodes and relations | Brain and AI platform |
| `knowledge_index.py` | Dataset search index | Search engine, AI platform |
| `search_engine.py` | Search facade | Conversation engine and AI platform |
| `brain.py`, `ai_platform.py` | Conversation/platform orchestration | Top-level `brain.py` and `main.py` |
| `format_handlers/` | Legacy file parsing | Dataset loader and knowledge factory |

## `main.py` and Spam Detection

`main.py` starts JARVIS, initializes TTS and microphone, creates `JarvisBrain`, then exposes a menu for voice/chat/spam/training. The existing `SpamDetector` uses joblib when `spam_detector.joblib` exists and falls back to rule-based scoring. The preprocessor combines subject, body, and email headers, cleans text, counts free words, URLs, urgency, verification language, and returns a spam score. The baseline listed scikit-learn and joblib dependencies. No model or dataset accuracy result was measurable in the baseline audit because no test, labeled model, and model artifact were present in the 98-file baseline snapshot.

## Test State

The baseline had no `tests/` directory and no pytest configuration. `pytest` could not be used to measure existing behavior in the original tree.

## Classification

| Module area | Decision | Reason |
|---|---|---|
| `config_manager.py` | KEEP/ADAPT | Useful for local paths and settings |
| `logger.py` | KEEP/ADAPT | Retain metadata-only logging; remove file/message logging |
| `validator.py` | KEEP/ADAPT | Reuse normalization and add hash/length validation |
| `memory_store.py` | ADAPT | Replace conversational/raw storage with privacy-safe feedback counts |
| Base extractor / registry and cleaning/normalization stages | ADAPT | Adapt the pattern to channel adapters and analysis stages |
| TXT and HTML extractor ideas | ADAPT | Reuse parsing concepts for plain text and email HTML |
| Existing `spam_detector.py` logic | ADAPT | Useful rule fallback; replace with structured threat scoring |
| `main.py` spam menu | ADAPT | Replace CLI with Flask web API |
| `dataset_manager/loader/watcher` | DELETE | Knowledge ingestion is not required |
| `knowledge_graph/index/factory/search_engine/brain/ai_platform` | DELETE | AI-KOS conversation/search architecture is unrelated |
| `schema_mapper/version/plugin/module/metadata/format handlers` | DELETE | No role in local scam detection |
| PDF/DOCX/CSV/JSON/MD/SQLite extractors | DELETE | Submission explicitly excludes these ingest paths |
| Voice/chat/TTS/speech modules | DELETE | Replaced by web channels |
| datasets, cache, logs, models, memory JSON | DELETE/IGNORE | Contain or may contain raw data; not needed |

## Dependency Audit

The baseline `requirements.txt` contained `scikit-learn`, `joblib`, and `pytest`. Scikit-learn and joblib are unnecessary unless a compatible legacy model under 2 MB is found and retained; the target is pure Python, offline Flask detection.

## 10-Line Summary

1. Baseline commit `5801955` was established on the `main` branch.
2. The repository was a modular AI-KOS/JARVIS application, not yet ScamShield.
3. No baseline file exceeded 500 KB.
4. The baseline included an existing rule/joblib spam detector.
5. No measurable model accuracy or working test suite was present.
6. Configuration, logging, validation, memory, extractor, and pipeline patterns can be adapted.
7. Dataset, knowledge graph, search, platform, voice, chat, and plugin modules are unrelated.
8. Raw memory/dataset files and log paths must not survive.
9. Flask, SQLite, the threat engine, channel adapters, and a static web UI are new.
10. Phase 1 may prune only after the baseline import audit.
