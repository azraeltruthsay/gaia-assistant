"""
chunk_creator.py

Handles creating document chunks from code content for vector database indexing.
"""

import os
import re
import ast
from typing import List, Dict
from langchain_core.documents import Document
import logging

logger = logging.getLogger("GAIA")

class ChunkCreator:
    """Creates document chunks from code content."""

    def create_chunks(self, filepath: str, content: str, language: str,
                      docstring: str = None, structure: Dict = None) -> List[Document]:
        """
        Create logical document chunks based on code structure.

        Args:
            filepath: Path to the code file
            content: Code content
            language: Detected language
            docstring: Optional docstring description
            structure: Optional code structure information

        Returns:
            List of Document objects
        """
        if not content:
            return []

        metadata = {
            'source': filepath,
            'language': language,
            'type': 'code',
            'line_count': len(content.splitlines())
        }

        if docstring:
            metadata['description'] = docstring
        if structure:
            metadata['structure'] = structure

        chunks = []

        # Base chunk
        base_chunk = Document(
            page_content=(
                f"Filename: {os.path.basename(filepath)}\n"
                f"Language: {language}\n"
                + (f"Description: {docstring}\n" if docstring else "")
                + f"Structure: {structure}"
            ),
            metadata=metadata.copy()
        )
        chunks.append(base_chunk)

        # Strategy: chunk by functions/classes if known, otherwise by lines
        if language == 'python':
            chunks.extend(self._create_python_chunks(content, metadata))
        elif language in ['javascript', 'typescript']:
            chunks.extend(self._create_js_chunks(content, metadata))
        else:
            chunks.extend(self._create_line_chunks(content, metadata))

        return chunks

    def _create_python_chunks(self, content: str, base_metadata: Dict) -> List[Document]:
        """Create chunks from Python classes/functions."""
        chunks = []
        try:
            tree = ast.parse(content)
            lines = content.splitlines()

            for node in tree.body:
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    start_line = node.lineno - 1
                    end_line = self._find_end_of_block(tree, node, len(lines))
                    chunk_lines = lines[start_line:end_line]
                    chunk_metadata = base_metadata.copy()
                    chunk_metadata.update({
                        'section_type': 'class' if isinstance(node, ast.ClassDef) else 'function',
                        'section_name': node.name,
                        'start_line': start_line + 1,
                        'end_line': end_line
                    })
                    chunks.append(Document(page_content='\n'.join(chunk_lines),
                                            metadata=chunk_metadata))
        except Exception as e:
            logger.warning(f"Python chunking failed: {e}")
            chunks.extend(self._create_line_chunks(content, base_metadata))

        return chunks

    def _find_end_of_block(self, tree, node, total_lines) -> int:
        """Estimate the end line of a class or function."""
        sibling_nodes = [n for n in tree.body if hasattr(n, 'lineno') and n.lineno > node.lineno]
        if sibling_nodes:
            return min(n.lineno for n in sibling_nodes) - 1
        return total_lines

    def _create_js_chunks(self, content: str, base_metadata: Dict) -> List[Document]:
        """Create chunks from JavaScript/TypeScript functions and classes."""
        chunks = []
        lines = content.splitlines()
        sections = []

        # Regex-based detection
        for match in re.finditer(r'class\s+(\w+)', content):
            sections.append(('class', match.group(1), content[:match.start()].count('\n')))
        for match in re.finditer(r'function\s+(\w+)', content):
            sections.append(('function', match.group(1), content[:match.start()].count('\n')))
        for match in re.finditer(r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>', content):
            sections.append(('function', match.group(1), content[:match.start()].count('\n')))

        sections.sort(key=lambda x: x[2])

        for i, (section_type, name, start) in enumerate(sections):
            end = sections[i + 1][2] if i + 1 < len(sections) else len(lines)
            chunk_lines = lines[start:end]
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({
                'section_type': section_type,
                'section_name': name,
                'start_line': start + 1,
                'end_line': end
            })
            chunks.append(Document(page_content='\n'.join(chunk_lines),
                                    metadata=chunk_metadata))

        if not sections:
            chunks.extend(self._create_line_chunks(content, base_metadata))

        return chunks

    def _create_line_chunks(self, content: str, base_metadata: Dict) -> List[Document]:
        """Fallback: split content by lines with overlap."""
        chunks = []
        lines = content.splitlines()
        chunk_size = 50
        overlap = 10

        for i in range(0, len(lines), chunk_size - overlap):
            end = min(i + chunk_size, len(lines))
            chunk_lines = lines[i:end]
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({
                'section_type': 'line_chunk',
                'start_line': i + 1,
                'end_line': end
            })
            chunks.append(Document(page_content='\n'.join(chunk_lines),
                                    metadata=chunk_metadata))

        return chunks
