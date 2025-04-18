"""
Code analyzer module for GAIA D&D Campaign Assistant.
Handles processing, analyzing, and indexing code files.
"""

import os
import re
import logging
from typing import List, Dict, Optional, Any
import ast
import tokenize
import io

from langchain_core.documents import Document
from app.utils.helpers import sanitize_filename, get_file_extension

# Get the logger
logger = logging.getLogger("GAIA")

class CodeAnalyzer:
    """Analyzes and processes code files for GAIA."""
    
    def __init__(self, config, llm=None):
        """
        Initialize with configuration and optional language model.
        
        Args:
            config: Configuration object
            llm: Optional language model for code analysis
        """
        self.config = config
        self.llm = llm
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
    
    def load_code_file(self, filepath: str) -> Optional[str]:
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
    
    def identify_language(self, filepath: str) -> str:
        """
        Identify the programming language of a file.
        
        Args:
            filepath: Path to the code file
            
        Returns:
            Language identifier string
        """
        extension = get_file_extension(filepath).lower()
        
        # Handle special cases
        if extension == '':
            # No extension, try to guess from the filename
            filename = os.path.basename(filepath).lower()
            if filename in ['dockerfile', 'makefile', 'gemfile', 'rakefile']:
                return filename
            
            # Try to analyze the content
            return self._guess_language_from_content(filepath)
        
        # Look up in supported extensions
        return self.supported_extensions.get(extension, 'unknown')
    
    def _guess_language_from_content(self, filepath: str) -> str:
        """
        Guess the programming language from file content.
        
        Args:
            filepath: Path to the code file
            
        Returns:
            Language identifier string
        """
        content = self.load_code_file(filepath)
        if not content:
            return 'unknown'
        
        # Simple heuristics for language detection
        if content.startswith('#!/bin/bash') or content.startswith('#!/bin/sh'):
            return 'shell'
        elif content.startswith('#!/usr/bin/env python'):
            return 'python'
        elif content.startswith('<?php'):
            return 'php'
        
        # Try to detect Python
        try:
            ast.parse(content)
            return 'python'
        except:
            pass
        
        # More complex heuristics could be added here
        
        return 'unknown'
    
    def extract_docstring(self, content: str, language: str) -> Optional[str]:
        """
        Extract docstring from code content.
        
        Args:
            content: Code content
            language: Language identifier
            
        Returns:
            Extracted docstring or None if not found
        """
        if language == 'python':
            return self._extract_python_docstring(content)
        elif language in ['javascript', 'typescript']:
            return self._extract_js_docstring(content)
        else:
            # For other languages, try generic comment extraction
            return self._extract_generic_comments(content, language)
    
    def _extract_python_docstring(self, content: str) -> Optional[str]:
        """Extract docstring from Python code."""
        try:
            tree = ast.parse(content)
            
            # Check for module docstring
            if len(tree.body) > 0 and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Str):
                return tree.body[0].value.s
            
            # No module docstring, try classes and functions
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                    return node.body[0].value.s
            
            return None
        except:
            # Fallback to regex for syntax errors
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if docstring_match:
                return docstring_match.group(1).strip()
            return None
    
    def _extract_js_docstring(self, content: str) -> Optional[str]:
        """Extract docstring from JavaScript or TypeScript code."""
        # Look for JSDoc comments
        jsdoc_match = re.search(r'/\*\*(.*?)\*/', content, re.DOTALL)
        if jsdoc_match:
            return jsdoc_match.group(1).strip()
        
        # Look for multiline comments
        multiline_match = re.search(r'/\*(.*?)\*/', content, re.DOTALL)
        if multiline_match:
            return multiline_match.group(1).strip()
        
        return None
    
    def _extract_generic_comments(self, content: str, language: str) -> Optional[str]:
        """Extract comments from generic code."""
        # Different comment styles
        comment_patterns = {
            'html': r'<!--(.*?)-->',
            'css': r'/\*(.*?)\*/',
            'shell': r'#.*',
            'yaml': r'#.*',
            'dockerfile': r'#.*',
        }
        
        pattern = comment_patterns.get(language)
        if not pattern:
            # Default to multiline C-style comments
            pattern = r'/\*(.*?)\*/'
        
        comments = re.findall(pattern, content, re.DOTALL)
        if comments:
            return '\n'.join([c.strip() for c in comments])
        
        return None
    
    def extract_code_structure(self, content: str, language: str) -> Dict[str, Any]:
        """
        Extract structure information from code content.
        
        Args:
            content: Code content
            language: Language identifier
            
        Returns:
            Dictionary with code structure information
        """
        if language == 'python':
            return self._extract_python_structure(content)
        elif language in ['javascript', 'typescript']:
            return self._extract_js_structure(content)
        else:
            # For other languages, provide basic structure
            return self._extract_generic_structure(content, language)
    
    def _extract_python_structure(self, content: str) -> Dict[str, Any]:
        """Extract structure from Python code."""
        structure = {
            'imports': [],
            'classes': [],
            'functions': [],
            'variables': []
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        structure['imports'].append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for name in node.names:
                        structure['imports'].append(f"{module}.{name.name}")
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    }
                    structure['classes'].append(class_info)
                elif isinstance(node, ast.FunctionDef) and node.parent_field != 'body':
                    # Only add top-level functions
                    structure['functions'].append(node.name)
                elif isinstance(node, ast.Assign) and node.parent_field == 'body':
                    # Only add top-level variables
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            structure['variables'].append(target.id)
        except:
            # Fallback for syntax errors
            pass
        
        return structure
    
    def _extract_js_structure(self, content: str) -> Dict[str, Any]:
        """Extract structure from JavaScript or TypeScript code."""
        structure = {
            'imports': [],
            'classes': [],
            'functions': [],
            'variables': []
        }
        
        # Simple regex-based extraction (a proper parser would be better in production)
        # Find imports
        imports = re.findall(r'import\s+(?:{[^}]*}|[^{;]*)\s+from\s+[\'"]([^\'"]*)[\'"]', content)
        structure['imports'] = imports
        
        # Find classes
        class_matches = re.findall(r'class\s+(\w+)', content)
        structure['classes'] = [{'name': name, 'methods': []} for name in class_matches]
        
        # Find functions
        function_matches = re.findall(r'function\s+(\w+)', content)
        arrow_function_matches = re.findall(r'const\s+(\w+)\s+=\s+\([^)]*\)\s+=>', content)
        structure['functions'] = function_matches + arrow_function_matches
        
        # Find variables
        variable_matches = re.findall(r'(?:const|let|var)\s+(\w+)\s+=', content)
        structure['variables'] = variable_matches
        
        return structure
    
    def _extract_generic_structure(self, content: str, language: str) -> Dict[str, Any]:
        """Extract basic structure from generic code."""
        # Very basic structure extraction
        structure = {
            'line_count': len(content.splitlines()),
            'size_bytes': len(content),
            'language': language
        }
        
        return structure
    
    def create_code_chunks(self, filepath: str, content: str) -> List[Document]:
        """
        Create chunks from code file for the vector database.
        
        Args:
            filepath: Path to the code file
            content: Code content
            
        Returns:
            List of document chunks for indexing
        """
        if not content:
            return []
            
        language = self.identify_language(filepath)
        docstring = self.extract_docstring(content, language)
        structure = self.extract_code_structure(content, language)
        
        # Create metadata
        metadata = {
            'source': filepath,
            'language': language,
            'type': 'code',
            'line_count': len(content.splitlines()),
        }
        
        if docstring:
            metadata['description'] = docstring
        
        # Create chunks based on the code's structure
        chunks = []
        
        # Base chunk with the document info
        base_chunk = Document(
            page_content=f"Filename: {os.path.basename(filepath)}\nLanguage: {language}\n" + 
                        (f"Description: {docstring}\n" if docstring else "") +
                        f"Structure: {structure}",
            metadata=metadata.copy()
        )
        chunks.append(base_chunk)
        
        # Split by logical functions/classes for better semantic retrieval
        if language == 'python':
            chunks.extend(self._create_python_chunks(filepath, content, metadata))
        elif language in ['javascript', 'typescript']:
            chunks.extend(self._create_js_chunks(filepath, content, metadata))
        else:
            # For other languages, split by lines with overlap
            chunks.extend(self._create_line_chunks(filepath, content, metadata))
        
        return chunks
    
    def _create_python_chunks(self, filepath: str, content: str, base_metadata: Dict[str, Any]) -> List[Document]:
        """Create chunks from Python code."""
        chunks = []
        
        try:
            tree = ast.parse(content)
            lines = content.splitlines()
            
            # Process classes and top-level functions
            for node in tree.body:
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    # Get start and end lines
                    start_line = node.lineno - 1  # AST lines are 1-indexed
                    end_line = 0
                    
                    # Find end of the class/function
                    for possible_end_node in tree.body:
                        if possible_end_node.lineno > node.lineno and (end_line == 0 or possible_end_node.lineno < end_line):
                            end_line = possible_end_node.lineno - 1
                    
                    if end_line == 0:
                        end_line = len(lines)
                    
                    # Get the content of the class/function
                    chunk_content = '\n'.join(lines[start_line:end_line])
                    
                    # Create metadata for this chunk
                    chunk_metadata = base_metadata.copy()
                    chunk_metadata['section_type'] = 'class' if isinstance(node, ast.ClassDef) else 'function'
                    chunk_metadata['section_name'] = node.name
                    chunk_metadata['start_line'] = start_line + 1
                    chunk_metadata['end_line'] = end_line
                    
                    # Create the document
                    chunk_doc = Document(
                        page_content=chunk_content,
                        metadata=chunk_metadata
                    )
                    chunks.append(chunk_doc)
        except:
            # Fallback for syntax errors: split by common pattern markers
            chunks.extend(self._create_line_chunks(filepath, content, base_metadata))
        
        return chunks
    
    def _create_js_chunks(self, filepath: str, content: str, base_metadata: Dict[str, Any]) -> List[Document]:
        """Create chunks from JavaScript/TypeScript code."""
        chunks = []
        lines = content.splitlines()
        
        # Find class and function boundaries (simplified approach)
        section_starts = []
        
        # Find class declarations
        for match in re.finditer(r'class\s+(\w+)', content):
            section_starts.append({
                'type': 'class',
                'name': match.group(1),
                'start': content[:match.start()].count('\n'),
                'match': match
            })
        
        # Find function declarations
        for match in re.finditer(r'function\s+(\w+)', content):
            section_starts.append({
                'type': 'function',
                'name': match.group(1),
                'start': content[:match.start()].count('\n'),
                'match': match
            })
        
        # Find arrow functions
        for match in re.finditer(r'const\s+(\w+)\s+=\s+\([^)]*\)\s+=>', content):
            section_starts.append({
                'type': 'function',
                'name': match.group(1),
                'start': content[:match.start()].count('\n'),
                'match': match
            })
        
        # Sort by start line
        section_starts.sort(key=lambda x: x['start'])
        
        # Create chunks for each section
        for i, section in enumerate(section_starts):
            start_line = section['start']
            
            # Determine end line (next section or end of file)
            if i < len(section_starts) - 1:
                end_line = section_starts[i + 1]['start']
            else:
                end_line = len(lines)
            
            # Get content
            chunk_content = '\n'.join(lines[start_line:end_line])
            
            # Create metadata
            chunk_metadata = base_metadata.copy()
            chunk_metadata['section_type'] = section['type']
            chunk_metadata['section_name'] = section['name']
            chunk_metadata['start_line'] = start_line + 1
            chunk_metadata['end_line'] = end_line
            
            # Create chunk
            chunk_doc = Document(
                page_content=chunk_content,
                metadata=chunk_metadata
            )
            chunks.append(chunk_doc)
        
        # If no sections found, default to line-based chunking
        if not section_starts:
            chunks.extend(self._create_line_chunks(filepath, content, base_metadata))
        
        return chunks
    
    def _create_line_chunks(self, filepath: str, content: str, base_metadata: Dict[str, Any]) -> List[Document]:
        """Create chunks based on line numbers with overlap."""
        chunks = []
        lines = content.splitlines()
        
        # Use a reasonable chunk size and overlap
        chunk_size = 50  # lines per chunk
        overlap = 10     # lines of overlap between chunks
        
        # Create chunks
        for i in range(0, len(lines), chunk_size - overlap):
            # Get chunk lines
            end_idx = min(i + chunk_size, len(lines))
            chunk_lines = lines[i:end_idx]
            
            # Create metadata
            chunk_metadata = base_metadata.copy()
            chunk_metadata['section_type'] = 'line_chunk'
            chunk_metadata['start_line'] = i + 1
            chunk_metadata['end_line'] = end_idx
            
            # Create chunk
            chunk_doc = Document(
                page_content='\n'.join(chunk_lines),
                metadata=chunk_metadata
            )
            chunks.append(chunk_doc)
            
            # If we've reached the end, break
            if end_idx >= len(lines):
                break
        
        return chunks
    
    def analyze_code_with_llm(self, filepath: str, content: str) -> Optional[Dict[str, Any]]:
        """
        Use the LLM to analyze code and provide insights.
        
        Args:
            filepath: Path to the code file
            content: Code content
            
        Returns:
            Dictionary with analysis results or None if analysis fails
        """
        if not self.llm or not content:
            return None
        
        language = self.identify_language(filepath)
        
        try:
            # Prepare prompt for code analysis
            prompt = f"""Analyze the following code file and provide insights:

Filepath: {filepath}
Language: {language}

```{language}
{content}
```

Provide the following in your analysis:
1. Brief summary of what this code does
2. Key components or functions
3. Potential improvements or optimizations
4. Any bugs or issues you notice

Format your response as a structured JSON object with the following fields:
- summary: Brief description of the code's purpose
- components: Array of key components or functions
- improvements: Array of potential improvements
- issues: Array of potential bugs or issues
- complexity_rating: Numerical rating from 1-10 of code complexity

Response:"""
            
            # Get analysis from LLM
            analysis_text = self.llm(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'({.*})', analysis_text, re.DOTALL)
            if json_match:
                import json
                analysis_json = json.loads(json_match.group(1))
                return analysis_json
            
            # Fallback: create structured analysis manually
            return {
                'summary': analysis_text[:200] + '...' if len(analysis_text) > 200 else analysis_text,
                'components': [],
                'improvements': [],
                'issues': [],
                'complexity_rating': 5  # Default middle value
            }
        except Exception as e:
            logger.error(f"Error analyzing code with LLM: {e}")
            return None
    
    def process_codebase(self, codebase_path: str) -> List[Document]:
        """
        Process an entire codebase directory and create chunks for indexing.
        
        Args:
            codebase_path: Path to the codebase directory
            
        Returns:
            List of document chunks for indexing
        """
        if not os.path.exists(codebase_path):
            logger.error(f"Codebase path does not exist: {codebase_path}")
            return []
        
        # Directories/files to exclude
        exclude_patterns = [
            r'\.git',
            r'\.venv',
            r'venv',
            r'__pycache__',
            r'\.pytest_cache',
            r'\.idea',
            r'\.vscode',
            r'node_modules',
            r'\.DS_Store',
            r'__MACOSX',
            r'*.pyc',
            r'*.pyo',
            r'*.pyd',
            r'*.so',
            r'*.o',
            r'*.a',
            r'*.lib',
            r'*.dll',
            r'*.exe',
            r'*.bin',
            r'*.obj',
            r'*.msi',
            r'*.dat',
            r'*.db',
            r'*.sqlite',
            r'*.sqlite3',
            r'*.log',
            r'/logs/',
            r'*.md5',
            r'*.sha1',
            r'*.pkl',
            r'*.pickle',
            r'*.model',
            r'*.ckpt',
            r'*.pt',
            r'*.pth',
            r'*.gguf',
        ]
        
        # Compile exclude patterns
        exclude_regex = [re.compile(pattern) for pattern in exclude_patterns]
        
        all_chunks = []
        
        # Walk the directory
        for root, dirs, files in os.walk(codebase_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(regex.search(d) for regex in exclude_regex)]
            
            for file in files:
                # Skip excluded files
                if any(regex.search(file) for regex in exclude_regex):
                    continue
                
                filepath = os.path.join(root, file)
                
                # Only process text files
                if not self._is_text_file(filepath):
                    continue
                
                # Load the file content
                content = self.load_code_file(filepath)
                if not content:
                    continue
                
                # Create chunks for the file
                file_chunks = self.create_code_chunks(filepath, content)
                all_chunks.extend(file_chunks)
                
                logger.info(f"Processed code file: {filepath} - Created {len(file_chunks)} chunks")
        
        logger.info(f"Processed codebase at {codebase_path} - Total chunks: {len(all_chunks)}")
        return all_chunks
    
    def _is_text_file(self, filepath: str) -> bool:
        """Check if a file is a text file."""
        try:
            # Try to read the first few bytes as text
            with open(filepath, 'r', encoding='utf-8') as f:
                f.read(1024)
            return True
        except:
            # If it fails, it's probably not a text file
            return False