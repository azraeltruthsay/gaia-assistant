"""
base_analyzer.py

Central interface for code analysis operations in GAIA Assistant.
"""

import os
from typing import List, Optional, Dict
from langchain_core.documents import Document

from .language_detector import LanguageDetector
from .docstring_extractor import DocstringExtractor
from .structure_extractor import StructureExtractor
from .chunk_creator import ChunkCreator
from .llm_analysis import LLMAnalyzer
from .file_loader import FileLoader
from .snapshot_manager import SnapshotManager
from .file_scanner import load_code_tree

import logging
logger = logging.getLogger("GAIA")


class CodeAnalyzer:
    """Central analyzer for code understanding, chunking, and insights."""

    def __init__(self, config, llm=None):
        """
        Initialize the Code Analyzer.

        Args:
            config: Configuration object
            llm: Optional LLM model for deeper analysis
        """
        self.config = config
        self.llm = llm

        self.file_loader = FileLoader()
        self.language_detector = LanguageDetector()
        self.docstring_extractor = DocstringExtractor()
        self.structure_extractor = StructureExtractor()
        self.chunk_creator = ChunkCreator()
        self.llm_analyzer = LLMAnalyzer(llm)

        self.snapshot_manager = SnapshotManager()
        self.code_tree = {}

    def refresh_code_tree(self, root_path: str = "/app"):
        """Load live code files into memory for introspection and hashing."""
        logger.info("🧠 Refreshing GAIA code tree...")
        self.code_tree = load_code_tree(root_path)
        logger.info(f"✅ Loaded {len(self.code_tree)} code files")

    def review_codebase(self):
        """
        Compare current codebase to the last snapshot.
        Re-summarize and update only files that have changed.
    
        Returns:
            Number of files re-analyzed this session.
        """
        if not self.code_tree:
            logger.warning("⚠️ Code tree is empty. Call refresh_code_tree() first.")
            return

        logger.info("🔍 Checking codebase for changes...")
        changed_files = self.snapshot_manager.get_files_to_update(self.code_tree)
        if not changed_files:
            logger.info("✅ No changes detected since last snapshot.")
            return 0
    
        summaries = {}
        for path, content in changed_files.items():
            logger.info(f"✏️ Summarizing updated file: {path}")
            summary = self.summarize_file_content(path, content)
            # 📝 Save the summary as a markdown document for Tier 0
            summary_path = os.path.join(
                "/app/knowledge/system_reference/code_summaries",
                path.replace("/", "_") + ".md"
            )
            os.makedirs(os.path.dirname(summary_path), exist_ok=True)
            try:
                with open(summary_path, "w", encoding="utf-8") as f:
                    f.write(f"# Summary of `{path}`\n\n{summary}")
                logger.info(f"🗃️ Saved summary for {path} to markdown")
            except Exception as e:
                logger.warning(f"⚠️ Failed to write summary markdown for {path}: {e}")

            summaries[path] = summary
    
        logger.info(f"📝 Updating snapshot with {len(summaries)} files")
        new_snapshot = self.snapshot_manager.generate_snapshot(self.code_tree, summaries)
        self.snapshot_manager.update_snapshot_file(new_snapshot)
        # 📥 Load new summaries into Tier 0 vector store
        self.doc_processor.process_documents(
            "/app/knowledge/system_reference/code_summaries",
            tier="0_system_reference",
            project="gaia"
        )
        logger.info("📚 Code summary markdowns embedded into Tier 0 knowledge")

        return len(summaries)

    def summarize_file_content(self, filepath: str, content: str) -> str:
        """Run LLM analysis on in-memory file content."""
        language = self.language_detector.identify_language(filepath)
        analysis = self.llm_analyzer.analyze_code(filepath, content, language)
        return analysis.get("summary", "") if isinstance(analysis, dict) else str(analysis)

    def process_codebase(self, codebase_path: str) -> List[Document]:
        """
        Process an entire codebase directory into document chunks.

        Args:
            codebase_path: Path to codebase

        Returns:
            List of Document chunks
        """
        if not os.path.exists(codebase_path):
            logger.error(f"Codebase path does not exist: {codebase_path}")
            return []

        all_chunks = []
        exclude_patterns = [
            '.git', '.venv', 'venv', '__pycache__', 'node_modules',
            '.pytest_cache', '.idea', '.vscode', '__MACOSX',
            '.DS_Store', '*.pyc', '*.pyo', '*.pyd', '*.so',
            '*.o', '*.a', '*.lib', '*.dll', '*.exe', '*.bin',
            '*.obj', '*.msi', '*.dat', '*.db', '*.sqlite', '*.sqlite3',
            '*.log', '*.md5', '*.sha1', '*.pkl', '*.pickle',
            '*.model', '*.ckpt', '*.pt', '*.pth', '*.gguf'
        ]

        for root, dirs, files in os.walk(codebase_path):
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            for file in files:
                if any(pattern in file for pattern in exclude_patterns):
                    continue

                filepath = os.path.join(root, file)
                if not self.file_loader.is_text_file(filepath):
                    continue

                file_chunks = self.chunk_single_file(filepath)
                if file_chunks:
                    all_chunks.extend(file_chunks)

        logger.info(f"📦 Processed {len(all_chunks)} document chunks from {codebase_path}")
        return all_chunks

    def chunk_single_file(self, filepath: str) -> List[Document]:
        """
        Process a single file into document chunks.

        Args:
            filepath: Path to code file

        Returns:
            List of Document objects
        """
        content = self.file_loader.load_code_file(filepath)
        if not content:
            return []

        language = self.language_detector.identify_language(filepath, self.file_loader)
        docstring = self.docstring_extractor.extract_docstring(content, language)
        structure = self.structure_extractor.extract_structure(content, language)

        chunks = self.chunk_creator.create_chunks(filepath, content, language, docstring, structure)
        return chunks

    def analyze_single_file(self, filepath: str) -> Optional[Dict]:
        """
        Analyze a single code file with the LLM.

        Args:
            filepath: Path to the code file

        Returns:
            Dictionary with analysis or None
        """
        if not self.llm:
            logger.warning("LLM model not provided; skipping analysis")
            return None

        content = self.file_loader.load_code_file(filepath)
        if not content:
            return None

        language = self.language_detector.identify_language(filepath, self.file_loader)
        analysis = self.llm_analyzer.analyze_code(filepath, content, language)
        return analysis
