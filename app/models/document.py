"""
Document processing module for GAIA D&D Campaign Assistant.
Handles loading, preprocessing, and converting documents.
"""

import os
import logging
from typing import Optional, List
from datetime import datetime

# Document processing imports
from striprtf.striprtf import rtf_to_text
from docx import Document as DocxDocument
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
# Get the logger
logger = logging.getLogger("GAIA")

class DocumentProcessor:
    """Handles loading, preprocessing, and converting documents."""
    
    def __init__(self, config, llm=None):
        """
        Initialize with configuration and optional language model.
        
        Args:
            config: Configuration object
            llm: Optional language model for text conversion
        """
        self.config = config
        self.llm = llm
    
    def extract_text_from_file(self, filepath: str) -> Optional[str]:
        """
        Extract text content from various file formats.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Extracted text content or None if extraction fails
        """
        _, ext = os.path.splitext(filepath)
        try:
            if ext.lower() == ".txt":
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            elif ext.lower() == ".rtf":
                return self._extract_rtf(filepath)
            elif ext.lower() == ".docx":
                return self._extract_docx(filepath)
            elif ext.lower() == ".md":
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"Unsupported file format: {ext}")
                return None
        except Exception as e:
            logger.error(f"Error extracting text from {filepath}: {e}")
            return None
    
    def _extract_rtf(self, filepath: str) -> Optional[str]:
        """Extract text from RTF files with fallback encoding."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                rtf_content = f.read()
                return rtf_to_text(rtf_content)
        except UnicodeDecodeError:
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    rtf_content = f.read()
                    return rtf_to_text(rtf_content)
            except Exception as e:
                logger.error(f"Error extracting RTF with latin-1 encoding: {e}")
                return None
        except Exception as e:
            logger.error(f"Error extracting RTF with utf-8 encoding: {e}")
            return None
    
    def _extract_docx(self, filepath: str) -> Optional[str]:
        """Extract text from DOCX files."""
        try:
            doc = DocxDocument(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX: {e}")
            return None
    
    def convert_to_markdown(self, text: str) -> Optional[str]:
        """
        Convert plain text to structured markdown using the LLM.
        
        Args:
            text: Plain text content to convert
            
        Returns:
            Markdown formatted text or None if conversion fails
        """
        if not self.llm:
            logger.error("LLM not available for markdown conversion")
            return None
            
        prompt = f"""Convert the following text into a structured markdown document:
        
        {text}
        
        Create a logical organization with appropriate headers and formatting. 
        Use # for primary headers, ## for secondary headers, etc. 
        
        Markdown Output:
        """
        
        try:
            response = self.llm(prompt)
            return response
        except Exception as e:
            logger.error(f"Error during markdown conversion: {e}")
            return None
    
    def save_markdown(self, filepath: str, content: str) -> bool:
        """
        Save markdown content to a file.
        
        Args:
            filepath: Path where the file should be saved
            content: Markdown content to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved markdown to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving markdown to {filepath}: {e}")
            return False
    
    def load_and_preprocess_data(self, data_path: str) -> List[Document]:
        """
        Load and preprocess markdown documents from a directory.
        
        Args:
            data_path: Directory containing markdown files
            
        Returns:
            List of loaded and preprocessed documents
        """
        documents = []
        try:
            for filename in os.listdir(data_path):
                if filename.endswith(".md"):
                    filepath = os.path.join(data_path, filename)
                    try:
                        loader = TextLoader(filepath, encoding='utf-8')
                        documents.extend(loader.load())
                        logger.info(f"Loaded document: {filepath}")
                    except Exception as e:
                        logger.error(f"Error loading document {filepath}: {e}")
        except Exception as e:
            logger.error(f"Error accessing directory {data_path}: {e}")
        
        return documents
    
    def process_raw_data(self) -> None:
        """Process all raw data files and convert them to markdown."""
        if not self.llm:
            logger.error("LLM not available for raw data processing")
            return
            
        try:
            for filename in os.listdir(self.config.raw_data_path):
                filepath = os.path.join(self.config.raw_data_path, filename)
                logger.info(f"Processing raw file: {filepath}")
                
                raw_text = self.extract_text_from_file(filepath)
                if not raw_text:
                    logger.warning(f"Could not extract text from {filepath}")
                    continue
                    
                markdown_content = self.convert_to_markdown(raw_text)
                if not markdown_content:
                    logger.warning(f"Could not convert {filepath} to markdown")
                    continue
                    
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"converted_{os.path.splitext(filename)[0]}_{timestamp}.md"
                output_filepath = os.path.join(self.config.output_path, output_filename)
                
                self.save_markdown(output_filepath, markdown_content)
        except Exception as e:
            logger.error(f"Error processing raw data: {e}")
    
    def get_document_info(self, filepath: str):
        """
        Get metadata for a document file.
        
        Args:
            filepath: Path to the document file
            
        Returns:
            Dictionary with file metadata
        """
        try:
            filename = os.path.basename(filepath)
            mtime = os.path.getmtime(filepath)
            size = os.path.getsize(filepath)
            
            return {
                'name': filename,
                'path': filepath,
                'modified': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'size': size
            }
        except Exception as e:
            logger.error(f"Error getting document info for {filepath}: {e}")
            return None
            
    def process_documents(self, directory: str, tier: Optional[str] = None, project: Optional[str] = None) -> List[Document]:
        """
        Load and wrap documents from a directory with tier/project metadata.
        
        Args:
            directory: Path to the documents folder
            tier: Knowledge tier (e.g., '0_system_reference', '2_structured')
            project: Optional project name
            
        Returns:
            List of LangChain Document objects with metadata
        """
        documents = []
        
        if not os.path.isdir(directory):
            logger.warning(f"Directory not found or invalid: {directory}")
            return documents
    
        try:
            for filename in os.listdir(directory):
                if filename.endswith(".md"):
                    filepath = os.path.join(directory, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if not content.strip():
                                logger.warning(f"Empty file skipped: {filepath}")
                                continue
    
                            metadata = {
                                "filename": filename,
                                "source_path": filepath,
                                "tier": tier if tier else "unspecified",
                                "project": project or "global"
                            }
    
                            documents.append(Document(page_content=content, metadata=metadata))
                            logger.info(f"Loaded document with metadata: {metadata}")
                    except Exception as e:
                        logger.error(f"Failed to load file {filepath}: {e}")
        except Exception as e:
            logger.error(f"Error accessing directory {directory}: {e}")
        
        return documents