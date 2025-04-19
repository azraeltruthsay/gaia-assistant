"""
AI Manager module for GAIA D&D Campaign Assistant.
Core component that handles AI interaction, query processing, and artifact generation.
"""

import os
import re
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

# LangChain imports
from langchain_community.llms import LlamaCpp

# Import local modules
from app.models.document import DocumentProcessor
from app.models.vector_store import VectorStoreManager
from app.models.tts import SpeechManager
from app.utils.hardware_optimization import detect_hardware, optimize_config
from app.utils.conversation_manager import ConversationManager
from app.models.code_analyzer import CodeAnalyzer
from app.utils.background_processor import BackgroundProcessor

# Import the ProjectManager
from app.utils.project_manager import ProjectManager

# Get the logger
logger = logging.getLogger("GAIA")

class AIManager:
    """Main AI manager class for the GAIA Campaign Assistant."""
    
    def __init__(self, config):
        """
        Initialize the AI Manager.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.llm = None
        self.vector_store = None
        self.doc_processor = None
        self.vector_store_manager = None
        self.speech_manager = None
        self.conversation_manager = None
        self.conversation_history = []
        self.core_instructions = ""
        self.code_analyzer = None
        self.background_processor = None  # Will be initialized later
    
        # Initialize Project Manager
        self.project_manager = ProjectManager(config)
        
    def initialize(self) -> bool:
        """
        Initialize all components of the system.
        
        Returns:
            True if initialization is successful, False otherwise
        """
        all_initialized = False
        # Load core instructions
        self.core_instructions = self._load_core_instructions()
        if not self.core_instructions:
            logger.warning("Failed to load GAIA's core instructions")
        else:
            logger.info("GAIA's core instructions loaded")
        
        # Detect hardware and optimize configuration
        hardware_info = detect_hardware()
        optimize_config(self.config, hardware_info)
        
        # Initialize LLM
        try:
            self.llm = self._setup_llm()
            if not self.llm:
                return False
        except Exception as e:
            logger.error(f"Error setting up LLM: {e}")
            return False
        
        # Initialize components
        self.doc_processor = DocumentProcessor(self.config, self.llm)
        self.vector_store_manager = VectorStoreManager(self.config)
        self.speech_manager = SpeechManager(self.config)
        self.conversation_manager = ConversationManager(self.config, self.llm)
        self.code_analyzer = CodeAnalyzer(self.config, self.llm)
        
        
        # Process raw data
        self.doc_processor.process_raw_data()
        
        # Load or create vector store
        documents = self.doc_processor.load_and_preprocess_data(self.config.data_path)
        if not documents:
            logger.warning("No documents found to process")
        
        if os.path.exists(self.config.vector_db_path) and os.listdir(self.config.vector_db_path):
            self.vector_store = self.vector_store_manager.load_vector_store()
        else:
            self.vector_store = self.vector_store_manager.create_vector_store(documents)
        
        if not self.vector_store:
            logger.error("Failed to initialize vector store")
            return False
        
        # Check if all components are initialized
        all_initialized = (self.llm is not None and 
                  self.vector_store is not None and 
                  self.doc_processor is not None and 
                  self.vector_store_manager is not None)
                
        if all_initialized:
            # Initialize background processor
            self.initialize_background_processor()
        return all_initialized
        return True
    
    def _load_core_instructions(self) -> str:
        """
        Load core instructions from file.
        
        Returns:
            Content of the instructions file or empty string if loading fails
        """
        # First try to get instructions from the project manager
        if hasattr(self, 'project_manager'):
            instructions = self.project_manager.get_project_instructions()
            if instructions:
                return instructions
        
        # Fallback to the standard instruction file
        try:
            with open(self.config.core_instructions_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Core instructions file not found at {self.config.core_instructions_file}")
            return ""
        except Exception as e:
            logger.error(f"Error reading core instructions file: {e}")
            return ""
    
    # Add this method to the AIManager class
    def initialize_background_processor(self):
        """Initialize the background processor for idle-time tasks."""
        try:
            self.background_processor = BackgroundProcessor(self.config, self)
            success = self.background_processor.start()
            if success:
                logger.info("Background processor initialized and started")
            else:
                logger.warning("Background processor initialization returned False")
            return success
        except Exception as e:
            logger.error(f"Error initializing background processor: {e}", exc_info=True)
            return False
    def register_user_activity(self):
        """Register user activity to inform the background processor."""
        if self.background_processor:
            self.background_processor.register_activity()
    
    def background_archive_conversation(self):
        """
        Archive the current conversation and schedule it for background processing.
        
        Returns:
            Summary information or None if operation failed
        """
        if not self.conversation_manager:
            logger.warning("Conversation manager not initialized")
            return None
            
        if not self.background_processor:
            logger.warning("Background processor not initialized")
            return None
        
        try:
            # Archive conversation
            archive_info = self.conversation_manager.summarize_and_archive_for_background()
            
            if not archive_info:
                logger.warning("Failed to archive conversation")
                return None
            
            # Add task to background processor
            self.background_processor.add_conversation_processing_task(
                archive_info["id"],
                archive_info["filepath"]
            )
            
            return {
                "id": archive_info["id"],
                "summary": archive_info["summary"],
                "status": "scheduled_for_processing"
            }
        except Exception as e:
            logger.error(f"Error archiving conversation for background processing: {e}", exc_info=True)
            return None
    
    
    def get_background_tasks_status(self):
        """
        Get status information about background tasks.
        
        Returns:
            Dictionary with task status information
        """
        if not self.background_processor:
            return {"error": "Background processor not initialized"}
        
        try:
            task_status = self.background_processor.get_task_status()
            archive_stats = self.conversation_manager.get_archive_statistics()
            
            return {
                "tasks": task_status,
                "archives": archive_stats
            }
        except Exception as e:
            logger.error(f"Error getting background tasks status: {e}", exc_info=True)
            return {"error": str(e)}
    
    # Add this method to the AIManager class
    def analyze_code(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a code file.
        
        Args:
            filepath: Path to the code file
            
        Returns:
            Dictionary with analysis results or None if analysis fails
        """
        
        self.register_user_activity()
        
        if not self.code_analyzer:
            logger.error("Code analyzer not initialized")
            return None
        
        try:
            # Load code file
            content = self.code_analyzer.load_code_file(filepath)
            if not content:
                logger.error(f"Failed to load code file: {filepath}")
                return None
            
            # Analyze the code
          analysis = self.code_analyzer.analyze_code_with_llm(filepath, content)
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing code: {e}", exc_info=True)
            return None
    
    # Add method to switch project context
    def switch_project(self, project_id: str) -> bool:
        """
        Switch to a different project context.
        
        Args:
            project_id: ID of the project to switch to
            
        Returns:
            True if successful, False otherwise
        """
        if not hasattr(self, 'project_manager'):
            logger.error("Project manager not initialized")
            return False
        
        try:
            # Switch project in project manager
            success = self.project_manager.switch_project(project_id)
            if not success:
                return False
            
            # Reload core instructions
            self.core_instructions = self._load_core_instructions()
            
            # Reload vector store with project-specific path
            if self.vector_store:
                self.vector_store_manager.config = self.config
                self.vector_store = self.vector_store_manager.load_vector_store()
            
            logger.info(f"Switched to project: {project_id}")
            return True
        except Exception as e:
            logger.error(f"Error switching projects: {e}")
            return False
    def _setup_llm(self) -> Optional[LlamaCpp]:
        """
        Set up the language model.
        
        Returns:
            Initialized LlamaCpp model or None if setup fails
        """
        if not os.path.exists(self.config.model_path):
            logger.error(f"Model file not found at: {self.config.model_path}")
            return None
        
        try:
            llm = LlamaCpp(
                model_path=self.config.model_path,
                n_gpu_layers=self.config.n_gpu_layers,
                n_ctx=self.config.n_ctx,
                n_batch=self.config.n_batch,
                n_threads=self.config.n_threads,
                f16_kv=True,
                verbose=False
            )
            logger.info(f"LLM initialized with model: {self.config.model_path}")
            logger.info(f"Using {self.config.n_threads} CPU threads")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return None
    
    def query_campaign_world(self, query: str) -> str:
        """
        Query the campaign world knowledge base.
        
        Args:
            query: User query string
            
        Returns:
            Response from the AI
        """
        # Add this at the beginning of the method
        self.register_user_activity()
        if not self.llm or not self.vector_store:
            return "System not fully initialized. Please check logs."
        
        try:
            # Add query to conversation manager
            if self.conversation_manager:
                self.conversation_manager.add_message("user", query)
            
            # Get relevant documents manually
            relevant_docs = self.vector_store_manager.get_relevant_documents(
                self.vector_store, query, k=5
            )
            
            # Format the documents as context
            context_text = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # Get relevant context from previous conversations
            previous_context = ""
            if self.conversation_manager:
                previous_context = self.conversation_manager.get_relevant_context_for_query(query)
            
            # Build prompt with VERY clear instructions against fabricated dialogue
            prompt = f"""You are GAIA, an AI assistant integrated into Rupert Roads' Warforged body.

    CRITICAL INSTRUCTION: This is a DIRECT conversation with Rupert. You must:
    1. Respond ONLY as yourself (GAIA) talking to Rupert
    2. NEVER create fictional dialogue
    3. NEVER include phrases like "Rupert says" or "Rupert asks"
    4. NEVER include "GAIA:" or similar prefixes
    5. NEVER create a back-and-forth conversation
    6. NEVER assume what Rupert might say or respond
    
    {self.core_instructions}
    
    {previous_context}
    
    BASE YOUR RESPONSE ONLY ON THE FOLLOWING CONTEXT:
    {context_text}
    
    Rupert is asking you: {query}
    
    Your direct response to Rupert:"""
            
            # Query the LLM directly
            response = self.llm(prompt)
            
            # Comprehensive cleanup
            response = self._clean_response(response)
            
            # Add response to conversation manager
            if self.conversation_manager:
                self.conversation_manager.add_message("assistant", response)
            
            return response
        
        except Exception as e:
            logger.error(f"Error in direct LLM query: {e}")
            # Fallback to a simple direct query
        
    def _clean_response(self, response: str) -> str:
        """
        Clean and format the LLM response.
        
        Args:
            response: Raw response from the LLM
            
        Returns:
            Cleaned response
        """
        # Comprehensive cleanup
        response = response.strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "GAIA:", 
            "Answer:", 
            "Response:", 
            "AI:", 
            "Assistant:", 
            "Here's the answer:"
        ]
        
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        # Remove any synthetic conversation markers
        if "Human:" in response or "GAIA:" in response or "User:" in response or "Rupert:" in response:
            parts = re.split(r'(?:Human:|GAIA:|User:|Rupert:)', response)
            response = parts[0].strip()
            
        # Remove any fictional dialogue patterns - more comprehensive
        dialogue_patterns = [
            r"Rupert(?:'s)? (?:response|says|asks|replied|questioned|stated|inquires|wonders|requests):",
            r"GAIA(?:'s)? (?:response|says|replies|answered|stated|responds|explains|notes):",
            r"User(?:'s)? (?:response|says|asks|replied|questioned|stated):",
            r"Human(?:'s)? (?:response|says|asks|replied|questioned|stated):"
        ]
        
        for pattern in dialogue_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                # Take only the first part before any dialogue markers
                parts = re.split(pattern, response, flags=re.IGNORECASE)
                response = parts[0].strip()
                break
        
        # Also check for numbered list format that might be part of fabricated dialogue
        if re.search(r'\d+\.\s+\*\*[^*]+\*\*:', response):
            # This looks like a numbered list with dialogue - take just the beginning
            parts = re.split(r'\d+\.\s+\*\*[^*]+\*\*:', response)
            response = parts[0].strip()
        
        # Also check for common fabricated dialogue patterns without explicit markers
        if "Your response to Rupert:" in response:
            parts = response.split("Your response to Rupert:")
            if len(parts) > 1:
                response = parts[1].strip()
        
        # Check if response appears to be cut off mid-sentence
        last_char = response[-1] if response else ""
        if last_char and last_char not in ".!?":
            # Find the last complete sentence if possible
            last_period = max(response.rfind('.'), response.rfind('!'), response.rfind('?'))
            if last_period > len(response) * 0.7:  # Only truncate if we've got most of the content
                response = response[:last_period+1]
        
        return response
    
    def generate_artifact(self, artifact_prompt: str) -> Optional[str]:
        """
        Generate a campaign artifact.
        
        Args:
            artifact_prompt: Prompt describing the artifact to generate
            
        Returns:
            Path to the saved artifact or None if generation fails
        """
        # Add this at the beginning of the method
        self.register_user_activity()
        if not self.llm:
            logger.error("LLM not available for artifact generation")
            return None
        
        try:
            # Limit conversation history to prevent context overflow
            limited_history = self.conversation_history[-self.config.MAX_HISTORY_LENGTH:]
            history_text = "\n".join(limited_history)
            
            # Get additional context from conversation manager
            conversation_context = ""
            if self.conversation_manager:
                conversation_context = self.conversation_manager.get_active_context()
            
            # Include a clear instruction to generate content as GAIA for Rupert
            full_prompt = (
                f"{self.core_instructions}\n\n"
                f"You are GAIA generating an artifact for Rupert Roads. "
                f"Artifact Generation Prompt: {artifact_prompt}\n\n"
                f"Create this artifact in clear markdown format.\n\n"
                f"Additional Context from Conversation:\n{conversation_context}\n\n"
                f"Conversation History:\n{history_text}"
            )
            
            response = self.llm(full_prompt)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"artifact_{timestamp}.md"
            filepath = os.path.join(self.config.output_path, filename)
            
            if self.doc_processor.save_markdown(filepath, response):
                logger.info(f"Artifact saved to: {filepath}")
                
                # Update vector store with new artifact
                new_documents = self.doc_processor.load_and_preprocess_data(self.config.output_path)
                if new_documents:
                    self.vector_store_manager.update_vector_store(self.vector_store, new_documents)
                    
                return filepath
            else:
                return None
        except Exception as e:
            logger.error(f"Error generating artifact: {e}")
            return None
    
    def extract_proper_name(self, query: str) -> Optional[str]:
        """
        Extract a properly capitalized name from a user introduction.
        
        Args:
            query: User query string
            
        Returns:
            Properly capitalized name or None if no name found
        """
        # Convert to lowercase for consistent pattern matching
        query_lower = query.lower()
        
        # Different introduction patterns
        patterns = [
            r"(?:i am|my name is|this is|i'm) ([^\.,;!?]+)",
            r"(?:called|known as) ([^\.,;!?]+)",
        ]
        
        for pattern in patterns:
            name_matches = re.findall(pattern, query_lower)
            if name_matches:
                lower_name = name_matches[0].strip()
                
                # Find position in original text to preserve capitalization
                start_pos = query_lower.find(lower_name)
                if start_pos != -1:
                    # Extract the properly capitalized name from the original query
                    return query[start_pos:start_pos + len(lower_name)].strip()
                
                # Fallback: Use title case as reasonable guess for proper nouns
                return lower_name.title()
        
        return None
    
    def classify_query(self, query: str) -> str:
        """
        Classify the type of query to determine how to handle it.
        
        Args:
            query: User query string
            
        Returns:
            Query classification type
        """
        query_lower = query.lower()
        
        # Greeting patterns
        greeting_patterns = [
            "hello", "hi ", "hey", "greetings", "good morning", "good afternoon", 
            "good evening", "howdy", "what's up"
        ]
        
        # Introduction patterns
        introduction_patterns = [
            "i am", "my name is", "this is", "i'm", "it's me"
        ]
        
        # Character-specific patterns (adjust based on your campaign)
        character_patterns = [
            "rupert", "roads", "anton", "snark", "gaia"
        ]
        
        # Question patterns
        question_patterns = [
            "what", "how", "why", "when", "where", "who", "can you", "tell me"
        ]
        
        # Classify the query
        if any(pattern in query_lower for pattern in greeting_patterns):
            if any(pattern in query_lower for pattern in introduction_patterns):
                return "greeting_with_introduction"
            if any(pattern in query_lower for pattern in character_patterns):
                return "greeting_with_character"
            return "greeting"
        
        if any(pattern in query_lower for pattern in question_patterns):
            return "question"
        
        # Default to information query
        return "information"
    
    def add_to_history(self, message: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            message: Message to add to history
        """
        # Keep legacy history for backward compatibility
        self.conversation_history.append(message)
        if len(self.conversation_history) > self.config.MAX_HISTORY_LENGTH * 2:
            self.conversation_history = self.conversation_history[-self.config.MAX_HISTORY_LENGTH:]
        
        # If the message is in the format "User: message" or "GAIA: message"
        # Extract and add to conversation manager
        if self.conversation_manager:
            user_match = re.match(r"^User(?:\s*\(Rupert\))?\s*:\s*(.+)$", message, re.DOTALL)
            gaia_match = re.match(r"^GAIA\s*:\s*(.+)$", message, re.DOTALL)
            
            if user_match:
                self.conversation_manager.add_message("user", user_match.group(1).strip())
            elif gaia_match:
                self.conversation_manager.add_message("assistant", gaia_match.group(1).strip())
    
    def get_context_summary(self) -> str:
        """
        Get a summary of the conversation context.
        
        Returns:
            A formatted summary of the conversation context
        """
        if self.conversation_manager:
            return self.conversation_manager.get_active_context()
        else:
            return "\n".join(self.conversation_history[-self.config.MAX_HISTORY_LENGTH:])
    
    def summarize_and_archive_conversation(self) -> Optional[str]:
        """
        Force summarization and archiving of the current conversation.
        
        Returns:
            The summary of the archived conversation, or None if operation failed
        """
        if not self.conversation_manager:
            logger.warning("Conversation manager not initialized")
            return None
        
        try:
            self.conversation_manager.summarize_and_archive()
            if self.conversation_manager.summaries:
                return self.conversation_manager.summaries[-1]["summary"]
            return None
        except Exception as e:
            logger.error(f"Error summarizing and archiving conversation: {e}")
            return None
    
    def speak_response(self, text: str) -> None:
        """
        Speak a response using text-to-speech.
        
        Args:
            text: Text to speak
        """
        if self.speech_manager:
            self.speech_manager.speak(text)
    
    def shutdown(self) -> None:
        """Clean shutdown of AI components."""
        if self.speech_manager:
            self.speech_manager.stop()
        logger.info("AI Manager shutdown complete")
        # Add this to the shutdown method
        if self.background_processor:
            self.background_processor.stop()
            logger.info("Background processor stopped")