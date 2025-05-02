azrael@Alice-360:/mnt/c/The_GAIA_Project/gaia-assistant$ tree
.
├── Dockerfile
├── RAW
│   ├── Strauthauk.txt
│   ├── desktop.ini
│   ├── new 1.txt
│   ├── new 10.txt
│   ├── new 11.txt
│   ├── new 14.txt
│   ├── new 15.txt
│   ├── new 17.txt
│   ├── new 2.txt
│   ├── new 3.txt
│   ├── new 4.txt
│   ├── new 5.txt
│   ├── new 7.txt
│   ├── new 8.txt
│   └── new 9.txt
├── app
│   ├── __init__.py
│   ├── behavior
│   │   ├── __init__.py
│   │   ├── creation_manager.py
│   │   ├── helper.py
│   │   ├── manager.py
│   │   └── session.py
│   ├── commands
│   │   ├── __init__.py
│   │   ├── create_behavior_command.py
│   │   └── create_behavior_trigger.py
│   ├── config.py
│   ├── desktop.ini
│   ├── ethics
│   │   ├── __init__.py
│   │   ├── ethical_sentinel.py
│   │   └── self_reflection.py
│   ├── intent_detection.py
│   ├── knowledge
│   │   ├── index.json
│   │   ├── system_reference
│   │   │   ├── code_summaries
│   │   │   ├── declaration_of_artisanal_intelligence.md
│   │   │   ├── error_reference.md
│   │   │   ├── gaia_constitution.md
│   │   │   ├── gaia_future_vision_roadmap.md
│   │   │   ├── memory_tiers_spec.md
│   │   │   ├── self_reflection_map.md
│   │   │   └── table_of_scrolls.md
│   │   └── verifier.py
│   ├── main.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── ai_manager.py
│   │   ├── document.py
│   │   ├── tts.py
│   │   └── vector_store.py
│   ├── templates
│   │   ├── __init__.py
│   │   └── behavior_template.py
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
│   │   │   ├── base_analyzer.py
│   │   │   ├── chunk_creator.py
│   │   │   ├── docstring_extractor.py
│   │   │   ├── file_loader.py
│   │   │   ├── file_scanner.py
│   │   │   ├── language_detector.py
│   │   │   ├── llm_analysis.py
│   │   │   ├── snapshot_manager.py
│   │   │   └── structure_extractor.py
│   │   ├── conversation
│   │   │   ├── __init__.py
│   │   │   ├── archiver.py
│   │   │   ├── keywords.py
│   │   │   ├── manager.py
│   │   │   └── summarizer.py
│   │   ├── desktop.ini
│   │   ├── hardware_optimization.py
│   │   ├── helpers.py
│   │   ├── knowledge_index.json
│   │   ├── project_manager.py
│   │   └── status_tracker.py
│   └── web
│       ├── __init__.py
│       ├── desktop.ini
│       ├── error_handlers.py
│       ├── project_routes.py
│       ├── routes.py
│       ├── routes_additional.py
│       └── web_app.py
├── benchmark.py
├── code_uploader.py
├── debug-script.js
├── directory_structure.md
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
├── gaia_code_instructions.txt
├── gaia_gamer_instructions.txt
├── gaia_instructions.txt
├── logs
│   ├── gaia.log
│   └── gaia_web.log
├── personalities
│   ├── default_personality..dev.json
│   └── default_personality.json
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
│       │   ├── converted_Strauthauk_20250430_034128.md
│       │   └── desktop.ini
│       ├── core-documentation
│       │   ├── braeneage_general_info.md
│       │   ├── desktop.ini
│       │   ├── gaia_conversational_record.md
│       │   ├── gaia_mission_record_axuraud_engagement.md
│       │   ├── gaia_mission_record_axuraud_engagement_part_2.md
│       │   ├── gaia_system_status_update.md
│       │   ├── heimr_general_info.md
│       │   ├── mechaduellum_system_reference_document.md
│       │   ├── mission_and_operational_tracker.md
│       │   ├── rupert_roads_character_sheet_with_tactical_tracker.md
│       │   ├── sonic_artifice_designations.md
│       │   └── the_fabric_of_reality.md
│       ├── raw-data
│       │   └── desktop.ini
│       └── structured_archives
├── shared
│   ├── chroma_db
│   │   ├── 50787e2f-07c0-40c8-ac6a-0185a44553b4
│   │   │   ├── data_level0.bin
│   │   │   ├── header.bin
│   │   │   ├── length.bin
│   │   │   └── link_lists.bin
│   │   ├── chroma.sqlite3
│   │   ├── code
│   │   ├── default
│   │   │   ├── 0f0a5d0c-3508-4d91-bbe6-c86fef0d9451
│   │   │   │   ├── data_level0.bin
│   │   │   │   ├── header.bin
│   │   │   │   ├── length.bin
│   │   │   │   └── link_lists.bin
│   │   │   └── chroma.sqlite3
│   │   └── dnd
│   │       ├── cad58d7e-1c7a-4a9a-b8ed-d5fab6995174
│   │       │   ├── data_level0.bin
│   │       │   ├── header.bin
│   │       │   ├── length.bin
│   │       │   └── link_lists.bin
│   │       └── chroma.sqlite3
│   ├── instructions
│   │   ├── code_instructions.txt
│   │   ├── default_instructions.txt
│   │   ├── dnd_instructions.txt
│   │   └── gaia_instructions.txt
│   └── projects.json
├── static
│   ├── code-debug.html
│   ├── css
│   │   ├── code-fix.css
│   │   ├── desktop.ini
│   │   └── styles.css
│   ├── desktop.ini
│   └── js
│       ├── api.js
│       ├── app.js
│       ├── archives.js
│       ├── background.js
│       ├── background_processing_ui.js
│       ├── background_processing_ui.legacy.js
│       ├── chat-fix.js
│       ├── chat.js
│       ├── code-analyzer.js
│       ├── code-analyzer.legacy.js
│       ├── conversation_archives.js
│       ├── desktop.ini
│       ├── project_switcher.js
│       ├── startup.js
│       ├── troubleshoot.js
│       └── ui.js
├── templates
│   ├── desktop.ini
│   └── index.html
├── tools
│   ├── campaign-tools.py
│   └── desktop.ini
└── troubleshooting
    └── desktop.ini

53 directories, 165 files