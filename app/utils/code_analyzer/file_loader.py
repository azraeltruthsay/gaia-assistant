"""
file_loader.py

Handles loading code files and checking for text files.
"""

import os
import logging

logger = logging.getLogger("GAIA")

class FileLoader:
    def __init__(self):
        pass

    def load_code_file(self, filepath: str) -> str:
        """
        Load a code file's content.

        Args:
            filepath: Path to the code file

        Returns:
            File content as string or None if loading fails
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error loading file with latin-1 encoding: {e}")
                return None
        except Exception as e:
            logger.error(f"Error loading code file {filepath}: {e}")
            return None

    def is_text_file(self, filepath: str) -> bool:
        """
        Check if a file is a text file.

        Args:
            filepath: Path to the file

        Returns:
            True if text file, False otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                f.read(1024)
            return True
        except:
            return False
