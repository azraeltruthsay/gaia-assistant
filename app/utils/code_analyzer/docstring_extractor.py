"""
docstring_extractor.py

Handles extracting docstrings and comments from code files.
"""

import re
import ast
import logging

logger = logging.getLogger("GAIA")

class DocstringExtractor:
    """Extracts docstrings and comments from code content."""

    def extract_docstring(self, content: str, language: str) -> str:
        """
        Extracts a docstring or header comment based on the language.

        Args:
            content: Code content as a string
            language: Detected language (e.g., 'python', 'javascript')

        Returns:
            Extracted docstring or comment string, or None.
        """
        if language == 'python':
            return self._extract_python_docstring(content)
        elif language in ['javascript', 'typescript']:
            return self._extract_js_docstring(content)
        else:
            return self._extract_generic_comments(content, language)

    def _extract_python_docstring(self, content: str) -> str:
        """Extract Python module or class/function docstrings."""
        try:
            tree = ast.parse(content)

            if (len(tree.body) > 0 
                and isinstance(tree.body[0], ast.Expr) 
                and isinstance(tree.body[0].value, ast.Str)):
                return tree.body[0].value.s

            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if (node.body 
                        and isinstance(node.body[0], ast.Expr) 
                        and isinstance(node.body[0].value, ast.Str)):
                        return node.body[0].value.s

            return None
        except Exception as e:
            logger.warning(f"AST parsing failed, fallback to regex: {e}")
            match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if match:
                return match.group(1).strip()
            return None

    def _extract_js_docstring(self, content: str) -> str:
        """Extract JSDoc-style comments from JavaScript or TypeScript."""
        match = re.search(r'/\*\*(.*?)\*/', content, re.DOTALL)
        if match:
            return match.group(1).strip()

        match = re.search(r'/\*(.*?)\*/', content, re.DOTALL)
        if match:
            return match.group(1).strip()

        return None

    def _extract_generic_comments(self, content: str, language: str) -> str:
        """Fallback comment extraction for other languages."""
        comment_patterns = {
            'html': r'<!--(.*?)-->',
            'css': r'/\*(.*?)\*/',
            'shell': r'#.*',
            'yaml': r'#.*',
            'dockerfile': r'#.*',
        }

        pattern = comment_patterns.get(language, r'/\*(.*?)\*/')
        matches = re.findall(pattern, content, re.DOTALL)

        if matches:
            return '\n'.join([match.strip() for match in matches])

        return None
