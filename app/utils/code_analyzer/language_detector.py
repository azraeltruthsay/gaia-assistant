"""
language_detector.py

Handles detecting programming language based on filename or file content.
"""

import os
import re
import ast
import logging
from app.utils.helpers import get_file_extension

logger = logging.getLogger("GAIA")

class LanguageDetector:
    def __init__(self):
        self.supported_extensions = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'html': 'html',
            'css': 'css',
            'md': 'markdown',
            'yml': 'yaml',
            'yaml': 'yaml',
            'json': 'json',
            'sh': 'shell',
            'bash': 'shell',
            'dockerfile': 'dockerfile',
        }

    def identify_language(self, filepath: str, file_loader=None) -> str:
        """
        Identify the programming language of a file.

        Args:
            filepath: Path to the code file
            file_loader: Optional FileLoader for loading content

        Returns:
            Language identifier string
        """
        extension = get_file_extension(filepath).lower()

        if extension == '':
            filename = os.path.basename(filepath).lower()
            if filename in ['dockerfile', 'makefile', 'gemfile', 'rakefile']:
                return filename
            if file_loader:
                return self._guess_language_from_content(filepath, file_loader)
            return 'unknown'

        return self.supported_extensions.get(extension, 'unknown')

    def _guess_language_from_content(self, filepath: str, file_loader) -> str:
        """
        Guess the programming language based on file content.
        """
        content = file_loader.load_code_file(filepath)
        if not content:
            return 'unknown'

        if content.startswith('#!/bin/bash') or content.startswith('#!/bin/sh'):
            return 'shell'
        elif content.startswith('#!/usr/bin/env python'):
            return 'python'
        elif content.startswith('<?php'):
            return 'php'

        try:
            ast.parse(content)
            return 'python'
        except:
            pass

        return 'unknown'
