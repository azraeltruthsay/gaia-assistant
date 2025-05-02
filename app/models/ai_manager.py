"""
AI Manager module for GAIA Assistant.
Core component that handles AI interaction, query processing, and artifact generation.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, List

from langchain_community.llms import LlamaCpp
from langchain_core.documents import Document

from app.models.document import DocumentProcessor
from app.models.vector_store import VectorStoreManager
from app.models.tts import SpeechManager
from app.utils.hardware_optimization import detect_hardware, optimize_config
from app.utils.conversation.manager import ConversationManager
from app.utils.code_analyzer import CodeAnalyzer
from app.utils.background.processor import BackgroundProcessor
from app.utils.helpers import clean_response
from app.utils.status_tracker import GAIA_STATUS

logger = logging.getLogger("GAIA")


class AIManager:
    def __init__(self, config):
        self.config = config
        self.llm = None
        self.vector_store = None
        self.doc_processor = None
        self.vector_store_manager = None
        self.speech_manager = None
        self.conversation_manager = None
        self.code_analyzer = None
        self.background_processor = None
        self.conversation_history = []
        self.personality = None
        self.initialized = False

    def initialize(self) -> bool:
        logger.info("🔧 Starting AI Manager initialization")
        GAIA_STATUS.update("Loading default personality...", 5)

        try:
            logger.info("📜 Loading default personality...")
            self.personality = self._load_default_personality()
            logger.info("✅ Default personality loaded")

            GAIA_STATUS.update("Optimizing hardware...", 10)
            logger.info("🧰 Detecting hardware and optimizing config...")
            hardware_info = detect_hardware()
            optimize_config(self.config, hardware_info)
            logger.info("✅ Hardware optimization complete")

            GAIA_STATUS.update("Loading LLM model...", 20)
            logger.info("📦 Setting up LLM...")
            self.llm = self._initialize_llm()
            logger.info("✅ LLM initialized")

            GAIA_STATUS.update("Initializing document processor...", 35)
            logger.info("🗂 Setting up document processor...")
            self.doc_processor = DocumentProcessor(self.config, self.llm)
            logger.info("✅ Document processor initialized")
            
            # ✅ Safe to load system reference docs now
            try:
                logger.info("📚 Loading system reference documents...")
                system_doc_path = "/app/knowledge/system_reference"
                self.doc_processor.process_documents(system_doc_path, tier="0_system_reference")
                logger.info("✅ System reference documents loaded")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load system reference docs: {e}")
            
                        
            GAIA_STATUS.update("Initializing vector store...", 50)
            logger.info("🧠 Setting up vector store manager...")
            self.vector_store_manager = VectorStoreManager(self.config)
            logger.info("✅ Vector store manager ready")

            logger.info("🎙 Trying to initialize speech manager...")
            self.speech_manager = self._try_initialize_component(SpeechManager)
            if self.speech_manager:
                logger.info("✅ Speech manager initialized")
            else:
                logger.warning("⚠️ Speech manager failed to initialize (optional)")

            GAIA_STATUS.update("Initializing conversation manager...", 65)
            logger.info("💬 Setting up conversation manager...")
            self.conversation_manager = ConversationManager(self.config, self.llm)
            logger.info("✅ Conversation manager ready")

            GAIA_STATUS.update("Initializing code analyzer...", 75)
            logger.info("🧪 Setting up code analyzer...")
            self.code_analyzer = CodeAnalyzer(self.config, self.llm)

            logger.info("📂 Refreshing live code tree...")
            self.code_analyzer.refresh_code_tree("/app")

            logger.info("🔍 Reviewing codebase for changes...")
            changed_count = self.code_analyzer.review_codebase()
            logger.info(f"🧠 GAIA introspected {changed_count} changed file(s) this session.")

            logger.info("✅ Code analyzer ready")

            GAIA_STATUS.update("Processing documents...", 85)
            logger.info("📑 Setting up background processor...")
            self.background_processor = BackgroundProcessor(self.config)
            logger.info("✅ Background processor created")

            logger.info("📁 Processing raw data...")
            self.doc_processor.process_raw_data()
            logger.info("✅ Raw data processed")

            logger.info("📄 Loading and preprocessing documents...")
            documents = self.doc_processor.load_and_preprocess_data(self.config.data_path)
            if not documents:
                logger.warning("⚠️ No documents found to process")

            logger.info("📦 Initializing vector store...")
            if os.path.exists(self.config.vector_db_path) and os.listdir(self.config.vector_db_path):
                logger.info("🔁 Loading existing vector store...")
                self.vector_store = self.vector_store_manager.load_vector_store()
            else:
                logger.warning("📦 No existing vector store found, creating new one...")
                self.vector_store = self.vector_store_manager.create_vector_store(documents) if documents else self.create_empty_vector_store()

            if self.vector_store is None:
                logger.error("❌ Vector store failed to initialize")
                raise RuntimeError("Failed to initialize vector store")

            GAIA_STATUS.update("Starting background processor...", 95)
            logger.info("🔄 Starting background processor...")
            self.initialize_background_processor()

            GAIA_STATUS.update("Initialization complete", 100)
            self.initialized = True
            logger.info("✅ AI Manager fully initialized")
            return True

        except Exception as e:
            logger.error(f"🔥 Critical error during AI Manager initialization: {e}", exc_info=True)
            self.initialized = False
            return False

    def _load_default_personality(self) -> dict:
        try:
            with open(self.config.default_personality_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Failed to load default personality: {e}", exc_info=True)
            raise

    def _initialize_llm(self):
        try:
            llm = LlamaCpp(
                model_path=self.config.model_path,
                n_gpu_layers=self.config.n_gpu_layers,
                n_ctx=self.config.n_ctx,
                n_threads=self.config.n_threads,
                verbose=False,
            )
            logger.info(f"✅ LLM loaded from {self.config.model_path}")
            return llm
        except Exception as e:
            logger.error(f"❌ Error initializing LLM: {e}", exc_info=True)
            raise

    def _try_initialize_component(self, component_class):
        try:
            return component_class(self.config)
        except Exception as e:
            logger.warning(f"⚠️ Optional component {component_class.__name__} failed to initialize: {e}")
            return None

    def initialize_background_processor(self) -> None:
        if self.background_processor:
            try:
                self.background_processor.ai_manager = self
                self.background_processor.conversation_manager = getattr(self, 'conversation_manager', None)
                self.background_processor.vector_store_manager = getattr(self, 'vector_store_manager', None)
                self.background_processor.vector_store = getattr(self, 'vector_store', None)
                self.background_processor.doc_processor = getattr(self, 'doc_processor', None)
                self.background_processor.start()
                logger.info("✅ Background processor started")
            except Exception as e:
                logger.error(f"❌ Error starting background processor: {e}", exc_info=True)
    
    def process_query(self, query_text: str) -> str:
        logger.info(f"📨 Processing query: {query_text}")
        try:
            response = self.query_campaign_world(query_text)
            cleaned_response = clean_response(response)
            self.conversation_manager.add_message("user", query_text)
            self.conversation_manager.add_message("assistant", cleaned_response)
            return cleaned_response
        except Exception as e:
            logger.error(f"❌ Error processing query: {e}", exc_info=True)
            return f"I encountered an error processing your request: {e}"

    def query_campaign_world(self, query_text: str) -> str:
        try:
            documents = self._get_relevant_documents(query_text)
            response = self._generate_response(query_text, documents)
            return response
        except Exception as e:
            logger.error(f"❌ Error in query_campaign_world: {e}", exc_info=True)
            return "I encountered an error processing your request."

    def _get_relevant_documents(self, query: str) -> List[Document]:
        if not self.vector_store:
            logger.warning("⚠️ Vector store not initialized")
            return []
    
        try:
            # Example: prioritize system reference knowledge + project documents
            filter_by = {"tier": {"$in": ["0_system_reference", "2_structured"]}}
            docs = self.vector_store_manager.get_relevant_documents(
                vector_store=self.vector_store,
                query=query,
                k=5,
                filter_by=filter_by
            )
            logger.info(f"🔍 Found {len(docs)} relevant documents (filtered)")
            return docs
        except Exception as e:
            logger.error(f"❌ Error fetching documents: {e}", exc_info=True)
            return []

    def _generate_response(self, query: str, documents: List[Document]) -> str:
        context = "\n".join(doc.page_content for doc in documents)
        prompt = f"{self.personality['system_prompt']}\nContext: {context}\nUser: {query}\nGAIA:"
        try:
            response = self.llm(prompt)
            return clean_response(response)
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}", exc_info=True)
            return "I encountered an error generating a response."

    
    def shutdown(self) -> None:
        if self.speech_manager:
            self.speech_manager.stop()
        if self.background_processor:
            self.background_processor.stop()
            logger.info("⛔ Background processor stopped")
        if self.conversation_manager:
            self.conversation_manager.summarize_and_archive()
            logger.info("💾 Final conversation archived on shutdown")
        logger.info("🔻 AI Manager shutdown complete")