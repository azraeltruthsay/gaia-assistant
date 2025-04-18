"""
Vector store module for GAIA D&D Campaign Assistant.
Manages document embeddings and retrieval functionality.
"""

import os
import logging
from typing import List, Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Get the logger
logger = logging.getLogger("GAIA")

class VectorStoreManager:
    """Manages the vector store for document embeddings and retrieval."""
    
    def __init__(self, config):
        """
        Initialize with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.embeddings = HuggingFaceEmbeddings(
            model_name=os.environ.get("EMBEDDING_MODEL", "all-mpnet-base-v2"),
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    def create_vector_store(self, documents: List[Document]) -> Optional[Chroma]:
        """
        Create a new vector store from documents.
        
        Args:
            documents: List of documents to embed
            
        Returns:
            Initialized Chroma vector store or None if creation fails
        """
        try:
            logger.info("Creating new vector store...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.CHUNK_SIZE, 
                chunk_overlap=self.config.CHUNK_OVERLAP
            )
            texts = text_splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} documents into {len(texts)} chunks")
            
            db = Chroma.from_documents(
                texts, 
                self.embeddings, 
                persist_directory=self.config.vector_db_path
            )
            db.persist()
            logger.info(f"Vector store created with {len(texts)} text chunks")
            return db
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            return None
    
    def load_vector_store(self) -> Optional[Chroma]:
        """
        Load an existing vector store.
        
        Returns:
            Loaded Chroma vector store or None if loading fails
        """
        try:
            logger.info("Loading existing vector store...")
            db = Chroma(
                persist_directory=self.config.vector_db_path,
                embedding_function=self.embeddings
            )
            logger.info("Vector store loaded successfully")
            return db
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return None
    
    def update_vector_store(self, vector_store: Chroma, new_documents: List[Document]) -> bool:
        """
        Update an existing vector store with new documents.
        
        Args:
            vector_store: Existing vector store to update
            new_documents: New documents to add to the store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.CHUNK_SIZE, 
                chunk_overlap=self.config.CHUNK_OVERLAP
            )
            texts = text_splitter.split_documents(new_documents)
            logger.info(f"Adding {len(texts)} new chunks to vector store")
            
            vector_store.add_documents(texts)
            vector_store.persist()
            logger.info("Vector store updated successfully")
            return True
        except Exception as e:
            logger.error(f"Error updating vector store: {e}")
            return False
    
    def get_relevant_documents(self, vector_store: Chroma, query: str, k: int = 5):
        """
        Get relevant documents for a query.
        
        Args:
            vector_store: Vector store to search
            query: Query string
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        try:
            retriever = vector_store.as_retriever(search_kwargs={"k": k})
            return retriever.get_relevant_documents(query)
        except Exception as e:
            logger.error(f"Error retrieving relevant documents: {e}")
            return []