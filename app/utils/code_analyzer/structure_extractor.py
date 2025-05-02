"""
structure_extractor.py

Handles extracting code structure like imports, classes, functions, and variables.
"""

import re
import ast
import logging

logger = logging.getLogger("GAIA")

class StructureExtractor:
    """Extracts structural information from code content."""

    def extract_structure(self, content: str, language: str) -> dict:
        """
        Extract code structure based on language.

        Args:
            content: Code content
            language: Detected language

        Returns:
            Dictionary with structure information
        """
        if language == 'python':
            return self._extract_python_structure(content)
        elif language in ['javascript', 'typescript']:
            return self._extract_js_structure(content)
        else:
            return self._extract_generic_structure(content, language)

    def _extract_python_structure(self, content: str) -> dict:
        """Extracts imports, classes, functions, and variables from Python code."""
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
                    structure['classes'].append({
                        'name': node.name,
                        'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    })
                elif isinstance(node, ast.FunctionDef):
                    structure['functions'].append(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            structure['variables'].append(target.id)

        except Exception as e:
            logger.warning(f"Python AST parsing failed: {e}")

        return structure

    def _extract_js_structure(self, content: str) -> dict:
        """Extracts imports, classes, functions, and variables from JS/TS code."""
        structure = {
            'imports': [],
            'classes': [],
            'functions': [],
            'variables': []
        }

        try:
            structure['imports'] = re.findall(r'import\s+(?:{[^}]*}|[^{;]*)\s+from\s+[\'"]([^\'"]+)[\'"]', content)
            structure['classes'] = [{'name': name, 'methods': []}
                                    for name in re.findall(r'class\s+(\w+)', content)]
            structure['functions'] = (re.findall(r'function\s+(\w+)', content) +
                                      re.findall(r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>', content))
            structure['variables'] = re.findall(r'(?:const|let|var)\s+(\w+)\s*=', content)
        except Exception as e:
            logger.warning(f"JS/TS structure parsing failed: {e}")

        return structure

    def _extract_generic_structure(self, content: str, language: str) -> dict:
        """Provides basic stats for unknown languages."""
        return {
            'line_count': len(content.splitlines()),
            'size_bytes': len(content.encode('utf-8')),
            'language': language
        }
