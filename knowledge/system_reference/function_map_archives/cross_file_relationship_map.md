# GAIA Cross-File Relationship Map (Updated)

---

## main.py
- Uses: /app/__init__.py (create_app, start_app)
- Uses: /app/models/ai_manager.py (initialize, run_self_analysis)

## runserver.py
- Uses: /main.py (main)
- Uses: /app/web/routes.py

## routes.py
- Uses: /app/web/project_routes.py
- Uses: /app/models/ai_manager.py (generate_response)
- Uses: /app/behavior/intent_detection.py
- Uses: /app/behavior/session_manager.py (sync_personas_with_behavior)
- Uses: /app/utils/knowledge_index.py
- Uses: /app/ethics/ethical_sentinel.py
- Uses: /app/ethics/core_identity_guardian.py
- Uses: /app/knowledge/verifier.py
- Uses: /app/utils/helpers.py
- Uses: /app/utils/conversation/archiver.py

## ai_manager.py
- Uses: /app/models/vector_store.py
- Uses: /app/models/document.py
- Uses: /app/behavior/session_manager.py
- Uses: /app/behavior/persona_manager.py
- Uses: /app/utils/status_tracker.py
- Uses: /app/utils/background/background_tasks.py

## background_tasks.py
- Uses: /app/models/vector_store.py
- Uses: /app/models/document.py
- Uses: /app/utils/conversation/summarizer.py

## persona_manager.py
- Uses: /app/behavior/session_manager.py
- Uses: /app/behavior/persona_writer.py

## code_analyzer/__init__.py
- Uses: base_analyzer.py, file_scanner.py, structure_extractor.py

## base_analyzer.py
- Uses: file_loader.py, docstring_extractor.py, snapshot_manager.py, llm_analysis.py

## project_manager.py
- Uses: /app/utils/knowledge_index.py
- Uses: /app/config.py

## initiative_handler.py
- Uses: /app/utils/topic_manager.py
- Uses: /app/config.py

## helpers.py
- Uses: /app/config.py (tier_names)

## routes_archive.py
- Uses: /app/web/archives.py

## self_analysis_trigger.py
- Uses: /app/models/ai_manager.py (run_self_analysis)

## persona_writer.py
- Uses: /app/models/vector_store.py

## session_manager.py
- Uses: /app/behavior/persona_manager.py
- Uses: /app/config.py
