gaia-assistant$ tree -I 'gaia_env|__pycache__|*.ini|*.sqlite3|*.bin|*.pyc'
.
├── =0.0.10
├── Dockerfile
├── app
│   ├── __init__ - Backup.py
│   ├── __init__.py
│   ├── behavior
│   │   ├── __init__.py
│   │   ├── creation_manager.py
│   │   ├── helper.py
│   │   ├── intent_detection.py
│   │   ├── persona_adapter.py
│   │   ├── persona_manager.py
│   │   └── persona_writer.py
│   ├── cli
│   │   └── cli_session.py
│   ├── cognition
│   │   ├── __init__.py
│   │   ├── cognitive_dispatcher.py
│   │   ├── council_dispatcher.py
│   │   ├── inner_monologue.py
│   │   ├── self_reflection.py
│   │   ├── telemetric_senses.py
│   │   └── topic_manager.py
│   ├── commands
│   │   ├── __init__.py
│   │   ├── create_persona_command.py
│   │   ├── create_persona_trigger.py
│   │   └── self_analysis_trigger.py
│   ├── config - Backup 2.py
│   ├── config - Backup.py
│   ├── config.py
│   ├── council
│   │   └── council_manager.py
│   ├── ethics
│   │   ├── __init__.py
│   │   ├── consent_protocol.py
│   │   ├── core_identity_guardian.py
│   │   └── ethical_sentinel.py
│   ├── gaia_constants.json
│   ├── memory
│   │   ├── __.init__.py
│   │   ├── conversation
│   │   │   ├── archiver.py
│   │   │   ├── keywords.py
│   │   │   ├── manager.py
│   │   │   └── summarizer.py
│   │   ├── dev_matrix.py
│   │   ├── knowledge_integrity.py
│   │   ├── priority_manager.py
│   │   ├── session_manager.py
│   │   └── status_tracker.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── ai_manager Backup 050425-0914.py
│   │   ├── ai_manager Backup 051325-0748.py
│   │   ├── ai_manager.py
│   │   ├── document.py
│   │   ├── tts.py
│   │   └── vector_store.py
│   ├── static
│   │   ├── __init__.py
│   │   ├── code-debug.html
│   │   ├── css
│   │   │   ├── __init__.py
│   │   │   ├── code-fix.css
│   │   │   └── styles.css
│   │   └── js
│   │       ├── __init__.py
│   │       ├── api.js
│   │       ├── app.js
│   │       ├── archives.js
│   │       ├── background.js
│   │       ├── background_processing_ui.js
│   │       ├── chat - Recent.js
│   │       ├── chat.js
│   │       ├── code-analyzer.js
│   │       ├── conversation_archives.js
│   │       ├── project_switcher.js
│   │       ├── startup.js
│   │       ├── troubleshoot.js
│   │       └── ui.js
│   ├── templates
│   │   ├── __init__.py
│   │   ├── index.html
│   │   └── persona_template.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── background
│   │   │   ├── __init__.py
│   │   │   ├── background_tasks.py
│   │   │   ├── idle_monitor.py
│   │   │   ├── processor.py
│   │   │   └── task_queue.py
│   │   ├── code_analyzer
│   │   │   ├── __init__.py
│   │   │   ├── audit_overview.md
│   │   │   ├── base_analyzer.py
│   │   │   ├── chunk_creator.py
│   │   │   ├── docstring_extractor.py
│   │   │   ├── file_loader.py
│   │   │   ├── file_scanner.py
│   │   │   ├── language_detector.py
│   │   │   ├── llm_analysis.py
│   │   │   ├── snapshot_manager.py
│   │   │   └── structure_extractor.py
│   │   ├── context.py
│   │   ├── gaia_rescue_helper.py
│   │   ├── hardware_optimization.py
│   │   ├── helpers.py
│   │   ├── knowledge_index.json
│   │   ├── knowledge_index.py
│   │   ├── output_sanitizer.py
│   │   ├── project_manager.py
│   │   ├── prompt_builder.py
│   │   ├── vector_indexer.py
│   │   └── verifier.py
│   └── web
│       ├── __init__.py
│       ├── archives.py
│       ├── error_handlers.py
│       ├── project_routes.py
│       ├── routes.py
│       └── routes_archive.py
├── benchmark.py
├── code_uploader.py
├── debug-script.js
├── docker-compose.yml
├── docs
│   ├── GAIA_Future_Vision_Roadmap.odt
│   ├── README.md
│   ├── background_processing_implementation_guide.txt
│   ├── gaia_assistant_project_documentation.txt
│   ├── gaia_enhancement_feasibility_assessment.txt
│   ├── gaia_error_handling_strategy.txt
│   ├── implementation-guide.md
│   ├── project-instructions.md
│   └── tier_5_expansion_plan.txt
├── gaia_rescue.py
├── knowledge
│   ├── __init__.py
│   ├── artifacts
│   ├── conversation_history
│   ├── core_docs
│   ├── hash_manifest.json
│   ├── index.json
│   ├── logs
│   │   ├── thoughtstream_2025-05-17.md
│   │   ├── thoughtstream_2025-05-18.md
│   │   ├── thoughtstream_2025-05-19.md
│   │   ├── thoughtstream_2025-05-20.md
│   │   ├── thoughtstream_2025-05-21.md
│   │   ├── thoughtstream_2025-05-22.md
│   │   ├── thoughtstream_2025-05-23.md
│   │   ├── thoughtstream_2025-05-24.md
│   │   ├── thoughtstream_2025-05-25.md
│   │   ├── thoughtstream_2025-05-26.md
│   │   ├── thoughtstream_2025-05-27.md
│   │   ├── thoughtstream_2025-05-29.md
│   │   └── thoughtstream_2025-05-30.md
│   ├── lora_adapters
│   ├── personas
│   │   ├── GAIA Default_persona.json
│   │   ├── code_analyzer
│   │   │   ├── code_analyzer_persona.json
│   │   │   └── instructions
│   │   │       └── code_analyzer_instructions.txt
│   │   ├── default
│   │   │   ├── default_persona.json
│   │   │   └── instructions
│   │   │       └── default_instructions.txt
│   │   └── dnd-campaign
│   │       ├── dnd-campaign_persona.json
│   │       └── instructions
│   │           └── dnd_instructions.txt
│   ├── projects
│   │   ├── default
│   │   │   ├── instructions
│   │   │   ├── raw_data
│   │   │   ├── structured
│   │   │   └── vector_store
│   │   ├── dnd-campaign
│   │   │   ├── instructions
│   │   │   ├── raw_data
│   │   │   ├── structured
│   │   │   └── vector_store
│   │   ├── gaia_rescue
│   │   │   └── last_session.json
│   │   └── session_history
│   ├── raw_data
│   │   ├── Strauthauk.txt
│   │   ├── new 1.txt
│   │   ├── new 10.txt
│   │   ├── new 11.txt
│   │   ├── new 14.txt
│   │   ├── new 15.txt
│   │   ├── new 17.txt
│   │   ├── new 2.txt
│   │   ├── new 3.txt
│   │   ├── new 4.txt
│   │   ├── new 5.txt
│   │   ├── new 7.txt
│   │   ├── new 8.txt
│   │   └── new 9.txt
│   ├── reflections
│   │   └── topic_cache.json
│   ├── structured
│   ├── system_reference
│   │   ├── GAIA_Function_Map
│   │   │   ├── dev_matrix_schema.md
│   │   │   ├── directory_tree.md
│   │   │   ├── gaia_functional_narrative - V2.md
│   │   │   ├── gaia_rescue_shell_functional_narrative.md
│   │   │   └── primitives_reference.md
│   │   ├── __init__.py
│   │   ├── coalition_of_minds.md
│   │   ├── code_summaries
│   │   │   └── __init__.py
│   │   ├── core_identity.json
│   │   ├── declaration_of_artisanal_intelligence.md
│   │   ├── dev_matrix.json
│   │   ├── error_reference.md
│   │   ├── function_map_archives
│   │   │   ├── chunk_1_core_system.md
│   │   │   ├── chunk_2_routes_api.md
│   │   │   ├── chunk_3_utilities.md
│   │   │   ├── chunk_4_models.md
│   │   │   ├── chunk_5_code_analyzer.md
│   │   │   ├── chunk_6_behavior_persona.md
│   │   │   ├── chunk_7_ethics_commands.md
│   │   │   ├── chunk_8_frontend_templates.md
│   │   │   ├── cross_file_relationship_map.md
│   │   │   ├── functions_reference_index.md
│   │   │   ├── gaia_functional_narrative - V1.md
│   │   │   └── gaia_functional_narrative - V2.md
│   │   ├── functions_reference.md
│   │   ├── gaia_constitution.md
│   │   ├── gaia_future_vision_roadmap.md
│   │   ├── hash_manifest.json
│   │   ├── layered_identity_model.md
│   │   ├── memory_tiers_spec.md
│   │   ├── mindscape_manifest.md
│   │   ├── persona_management_guide.md
│   │   ├── self_reflection_map.md
│   │   ├── table_of_scrolls.md
│   │   ├── thought_seeds
│   │   └── vector_store
│   │       └── gaia_rescue_index
│   │           ├── default__vector_store.json
│   │           ├── docstore.json
│   │           ├── graph_store.json
│   │           ├── image__vector_store.json
│   │           ├── index_store.json
│   │           └── vector_index_manifest.json
│   └── vectordb
│       └── 0be68820-e48a-46a9-b525-dc25e93403d7
├── logs
│   ├── 0503-Boot-Attempt3.log
│   ├── 0503-Boot-Attempt4.log
│   ├── 0503-Boot-Attempt6.log
│   ├── BackEnd Success Front End Failure 1.txt
│   ├── FirstBootAfterAudit-ErrorsAbout.log
│   ├── SecondBootAfterAudit-ErrorsAbout.log
│   ├── gaia.log
│   └── gaia_web.log
├── main.py
├── projects
│   ├── code-assistant
│   │   ├── conversation_archives
│   │   ├── core-documentation
│   │   ├── files
│   │   ├── output
│   │   ├── raw
│   │   └── structured_archives
│   ├── default
│   │   ├── conversation_archives
│   │   ├── converted_raw
│   │   ├── core-documentation
│   │   │   └── GAIA_Constitution.txt
│   │   ├── raw-data
│   │   └── structured_archives
│   └── dnd-campaign
│       ├── conversation_archives
│       ├── converted_raw
│       │   └── converted_Strauthauk_20250430_034128.md
│       ├── core-documentation
│       │   ├── braeneage_general_info.md
│       │   ├── gaia_conversational_record.md
│       │   ├── gaia_mission_record_axuraud_engagement.md
│       │   ├── gaia_mission_record_axuraud_engagement_part_2.md
│       │   ├── gaia_system_status_update.md
│       │   ├── heimr_general_info.md
│       │   ├── mechaduellum_system_reference_document.md
│       │   ├── mission_and_operational_tracker.md
│       │   ├── rupert-roads
│       │   │   ├── gaia_conversational_record.md
│       │   │   └── gaia_mission_record_axuraud_engagement.md
│       │   ├── rupert_roads_character_sheet_with_tactical_tracker.md
│       │   ├── sonic_artifice_designations.md
│       │   └── the_fabric_of_reality.md
│       ├── raw-data
│       └── structured_archives
├── requirements.txt
├── runserver.py
├── shared
│   ├── chroma_db
│   │   ├── 50787e2f-07c0-40c8-ac6a-0185a44553b4
│   │   ├── code
│   │   ├── default
│   │   │   └── 0f0a5d0c-3508-4d91-bbe6-c86fef0d9451
│   │   └── dnd
│   │       └── cad58d7e-1c7a-4a9a-b8ed-d5fab6995174
│   ├── instructions
│   │   ├── code_instructions.txt
│   │   └── gaia_instructions.txt
│   ├── projects.json
│   └── topic_cache.json
├── tools
│   └── campaign-tools.py
└── troubleshooting

90 directories, 229 files