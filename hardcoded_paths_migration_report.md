# Hardcoded Path Migration Report
Generated: Tue Aug 26 15:11:10 +08 2025
Project: .
Mode: DRY RUN
Total replacements: 142

## test_implementation.py
Replacements: 1

**Line 57:**
```python
# Before:
"build_data"
# After:
str(directory_manager.get_data_root())
```

## p3.py
Replacements: 5

**Line 47:**
```python
# Before:
"data/stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 68:**
```python
# Before:
"data/stage_00_original"
# After:
get_data_path(DataLayer.RAW_DATA)
```

**Line 68:**
```python
# Before:
"data/stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 68:**
```python
# Before:
"data/stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 82:**
```python
# Before:
"data/stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

## infra/create_pr_with_test.py
Replacements: 1

**Line 16:**
```python
# Before:
"build_data"
# After:
str(directory_manager.get_data_root())
```

## infra/cleanup_obsolete_files.py
Replacements: 3

**Line 111:**
```python
# Before:
"data/stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 112:**
```python
# Before:
"data/stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 113:**
```python
# Before:
"data/stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

## ETL/semantic_retrieval.py
Replacements: 3

**Line 116:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 142:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 212:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

## ETL/import_data.py
Replacements: 1

**Line 28:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

## ETL/sec_edgar_spider.py
Replacements: 1

**Line 56:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

## ETL/graph_data_integration.py
Replacements: 3

**Line 260:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 346:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 421:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

## ETL/update_data_paths.py
Replacements: 4

**Line 49:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 49:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 50:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 50:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

## ETL/build_dataset.py
Replacements: 15

**Line 68:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 80:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 94:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 102:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 110:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 113:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 122:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 125:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 270:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 280:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 285:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 316:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 322:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 327:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 512:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

## ETL/migrate_data_structure.py
Replacements: 1

**Line 27:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

## ETL/tests/test_data_structure.py
Replacements: 3

**Line 26:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 27:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 28:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

## ETL/tests/test_config.py
Replacements: 9

**Line 171:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 172:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 173:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 199:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 199:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 200:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 200:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 201:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 201:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

## ETL/tests/fixtures/test_data_fixtures.py
Replacements: 3

**Line 189:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 195:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 201:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

## tests/conftest.py
Replacements: 1

**Line 34:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

## tests/test_graph_rag_integration.py
Replacements: 1

**Line 276:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

## tests/test_release_manager.py
Replacements: 9

**Line 51:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 97:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 105:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 129:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 224:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 318:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 323:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 478:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 510:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

## tests/test_dataset_integrity.py
Replacements: 4

**Line 106:**
```python
# Before:
"data/stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 149:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 150:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 151:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

## tests/test_common_modules.py
Replacements: 3

**Line 161:**
```python
# Before:
"data/stage_99_build/build_20250812_100000"
# After:
str(get_build_path("20250812_100000"))
```

**Line 162:**
```python
# Before:
"data/stage_99_build/build_20250812_110000"
# After:
str(get_build_path("20250812_110000"))
```

**Line 163:**
```python
# Before:
"data/stage_99_build/build_20250812_120000"
# After:
str(get_build_path("20250812_120000"))
```

## tests/test_subtree_migration_simple.py
Replacements: 10

**Line 38:**
```python
# Before:
"build_data"
# After:
str(directory_manager.get_data_root())
```

**Line 71:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 74:**
```python
# Before:
"stage_00_original"
# After:
get_data_path(DataLayer.RAW_DATA)
```

**Line 109:**
```python
# Before:
"stage_00_original"
# After:
get_data_path(DataLayer.RAW_DATA)
```

**Line 110:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 111:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 112:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 113:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 188:**
```python
# Before:
"build_data"
# After:
str(directory_manager.get_data_root())
```

**Line 207:**
```python
# Before:
"build_data"
# After:
str(directory_manager.get_data_root())
```

## tests/test_directory_structure_protection.py
Replacements: 8

**Line 88:**
```python
# Before:
"build_data"
# After:
str(directory_manager.get_data_root())
```

**Line 108:**
```python
# Before:
"data/config"
# After:
str(get_config_path())
```

**Line 213:**
```python
# Before:
"data/config"
# After:
str(get_config_path())
```

**Line 315:**
```python
# Before:
"stage_00_original"
# After:
get_data_path(DataLayer.RAW_DATA)
```

**Line 316:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 317:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 318:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 319:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

## tests/e2e/test_module_integration.py
Replacements: 1

**Line 176:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

## graph_rag/setup_graph_rag.py
Replacements: 1

**Line 199:**
```python
# Before:
"data/stage_00_original"
# After:
get_data_path(DataLayer.RAW_DATA)
```

## common/quality_reporter.py
Replacements: 8

**Line 61:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 63:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 65:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 120:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 193:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 278:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 332:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 480:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

## common/utils.py
Replacements: 17

**Line 75:**
```python
# Before:
"stage_00_original"
# After:
get_data_path(DataLayer.RAW_DATA)
```

**Line 75:**
```python
# Before:
"stage_00_original"
# After:
get_data_path(DataLayer.RAW_DATA)
```

**Line 76:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 76:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 77:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 77:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 78:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 78:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 79:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 79:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 80:**
```python
# Before:
"stage_00_original"
# After:
get_data_path(DataLayer.RAW_DATA)
```

**Line 81:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 82:**
```python
# Before:
"stage_00_original"
# After:
get_data_path(DataLayer.RAW_DATA)
```

**Line 83:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 84:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 85:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 86:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

## common/build_tracker.py
Replacements: 7

**Line 66:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 73:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 80:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 185:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

**Line 187:**
```python
# Before:
"stage_02_transform"
# After:
get_data_path(DataLayer.DAILY_INDEX)
```

**Line 189:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

**Line 453:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

## common/tests/test_directory_manager.py
Replacements: 6

**Line 48:**
```python
# Before:
"build_data"
# After:
str(directory_manager.get_data_root())
```

**Line 69:**
```python
# Before:
"build_data"
# After:
str(directory_manager.get_data_root())
```

**Line 159:**
```python
# Before:
"stage_00_original"
# After:
get_data_path(DataLayer.RAW_DATA)
```

**Line 160:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 167:**
```python
# Before:
"build_data"
# After:
str(directory_manager.get_data_root())
```

**Line 226:**
```python
# Before:
"build_data"
# After:
str(directory_manager.get_data_root())
```

## common/tests/test_config_manager.py
Replacements: 1

**Line 66:**
```python
# Before:
"build_data"
# After:
str(directory_manager.get_data_root())
```

## scripts/manage_build_data.py
Replacements: 1

**Line 28:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

## scripts/release_manager.py
Replacements: 1

**Line 30:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

## evaluation/validate_development_environment.py
Replacements: 1

**Line 26:**
```python
# Before:
"stage_01_extract"
# After:
get_data_path(DataLayer.DAILY_DELTA)
```

## dcf_engine/sec_integration_template.py
Replacements: 2

**Line 35:**
```python
# Before:
"data/stage_00_original"
# After:
get_data_path(DataLayer.RAW_DATA)
```

**Line 514:**
```python
# Before:
"data/stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

## dcf_engine/build_knowledge_base.py
Replacements: 2

**Line 325:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 330:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

## dcf_engine/llm_dcf_generator.py
Replacements: 2

**Line 327:**
```python
# Before:
"data/stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

**Line 653:**
```python
# Before:
"data/stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```

## dcf_engine/rag_orchestrator.py
Replacements: 1

**Line 99:**
```python
# Before:
"stage_03_load"
# After:
get_data_path(DataLayer.GRAPH_RAG)
```

## dcf_engine/pure_llm_dcf.py
Replacements: 2

**Line 37:**
```python
# Before:
"stage_00_original"
# After:
get_data_path(DataLayer.RAW_DATA)
```

**Line 121:**
```python
# Before:
"stage_99_build"
# After:
get_data_path(DataLayer.QUERY_RESULTS)
```
