#!/usr/bin/env python3
"""
GAIA - D&D Campaign AI Assistant (CLI Entry Point)

This module provides a command-line interface for interacting with the GAIA
D&D Campaign AI Assistant.
"""

import os
import sys
import logging
from datetime import datetime

# Import application components
from app.config import Config
from app.models.ai_manager import AIManager
from app.utils.status_tracker import GAIA_STATUS

def main():
    """Main CLI function for GAIA."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/gaia_cli.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("GAIA_CLI")
    
    try:
        print("\nWelcome to GAIA - General Assistant - Intelligent Artifice!")
        print("Initializing the AI assistant... Please wait.")
        
        # Create config and AI manager
        config = Config()
        ai_manager = AIManager(config)
        
        # Initialize AI components
        if not ai_manager.initialize():
            logger.critical("Failed to initialize GAIA")
            print("Error: Failed to initialize GAIA. Check logs for details.")
            return 1
        
        print("\nGAIA is now initialized and ready to assist you!")
        print("Ask about your campaign world, request artifacts, or type 'exit' to quit.")
        print("Type 'artifact: <description>' to generate campaign artifacts.\n")
        
        # Main interaction loop
        while True:
            query = input("Ask about your campaign world: ")
            ai_manager.add_to_history(f"User (Rupert): {query}")
            
            if query.lower() == 'exit':
                print("Exiting GAIA. Goodbye!")
                ai_manager.shutdown()
                break
                
            elif query.lower().startswith('artifact:'):
                artifact_prompt = query[len('artifact:'):].strip()
                print("Generating artifact...")
                
                artifact_filepath = ai_manager.generate_artifact(artifact_prompt)
                if artifact_filepath:
                    print(f"Artifact saved to: {artifact_filepath}")
                else:
                    print("Failed to generate artifact.")
                    
            else:
                answer = ai_manager.query_campaign_world(query)
                print(f"\n{answer}\n")
                ai_manager.add_to_history(answer)
                ai_manager.speak_response(answer)
                
        return 0
        
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
        return 0
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        print(f"Critical error: {e}")
        return 1

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Run the application
    sys.exit(main())