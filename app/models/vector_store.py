"""
Vector store manager for GAIA Assistant.
Manages creation, loading, updating, and querying of document embeddings.
"""

import os
import logging
from typing import List, Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from sentence_transformers import SentenceTransformer

logger = logging.getLogger("GAIA")

class VectorStoreManager:
    """Manages the vector store for embeddings and semantic retrieval."""

    def __init__(self, config):
        self.config = config

        embedding_model_name = os.environ.get("EMBEDDING_MODEL", "all-mpnet-base-v2")
        device = "cpu"  # Force CPU for compatibility

        logger.info(f"📦 Preloading embedding model '{embedding_model_name}' on {device}...")
        preloaded_model = SentenceTransformer(embedding_model_name, device=device)

        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={"device": device},
            encode_kwargs={"normalize_embeddings": True},
            client=preloaded_model
        )

    def create_vector_store(self, documents: List[Document], persist: bool = True) -> Optional[Chroma]:
        """
        Create a new vector store from a list of tiered, metadata-rich documents.
    
        Args:
            documents: List of langchain Document objects
            persist: Whether to save the vector store to disk
    
        Returns:
            A Chroma vector store object or None on failure
        """
        try:
            logger.info("📂 Creating new vector store from documents...")
    
            # 🧼 Filter out empty or invalid documents
            valid_docs = [doc for doc in documents if doc.page_content and doc.page_content.strip()]
            if not valid_docs:
                logger.warning("⚠️ No valid documents to process. Skipping vector store creation.")
                return None
    
            # 🧩 Chunk the documents while retaining metadata
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.CHUNK_SIZE,
                chunk_overlap=self.config.CHUNK_OVERLAP
            )
            chunks = text_splitter.split_documents(valid_docs)
            logger.info(f"🧩 Split {len(valid_docs)} documents into {len(chunks)} chunks")
    
            # 🧠 Create Chroma vector store with preserved metadata
            db = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.config.vector_db_path
            )
    
            if persist:
                db.persist()
                logger.info(f"💾 Vector store persisted to: {self.config.vector_db_path}")
    
            logger.info("✅ Vector store created successfully")
            return db
    
        except Exception as e:
            logger.error(f"❌ Error creating vector store: {e}", exc_info=True)
            return None

    def load_vector_store(self) -> Optional[Chroma]:
        """Load an existing vector store from disk."""
        try:
            logger.info(f"📂 Loading vector store from: {self.config.vector_db_path}")
            if not os.path.exists(self.config.vector_db_path):
                logger.warning("⚠️ Vector store directory does not exist")
                return None

            db = Chroma(
                persist_directory=self.config.vector_db_path,
                embedding_function=self.embeddings
            )
            logger.info("✅ Vector store loaded successfully")
            return db
        except Exception as e:
            logger.error(f"❌ Error loading vector store: {e}", exc_info=True)
            return None

    def update_vector_store(self, vector_store: Chroma, new_documents: List[Document], persist: bool = True) -> bool:
        """Update a vector store with additional documents."""
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.CHUNK_SIZE,
                chunk_overlap=self.config.CHUNK_OVERLAP
            )
            chunks = text_splitter.split_documents(new_documents)
            logger.info(f"📥 Adding {len(chunks)} new chunks to vector store")

            vector_store.add_documents(chunks)
            if persist:
                vector_store.persist()
                logger.info("💾 Vector store changes persisted")

            logger.info("✅ Vector store updated successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Error updating vector store: {e}", exc_info=True)
            return False

    def get_relevant_documents(
        self,
        vector_store: Chroma,
        query: str,
        k: int = 5,
        filter_by: Optional[dict] = None
    ) -> List[Document]:
        """
        Retrieve top-k relevant documents using semantic similarity with optional metadata filtering.
    
        Args:
            vector_store: The Chroma instance to search
            query: User query string
            k: Number of results to return
            filter_by: Optional dictionary of metadata filters, e.g. {'tier': '0_system_reference'}
    
        Returns:
            List of relevant langchain Document objects
        """
        try:
            logger.info(f"🔎 Retrieving top {k} documents for query: '{query[:60]}...'")
    
            search_kwargs = {"k": k}
            if filter_by:
                search_kwargs["filter"] = filter_by
                logger.info(f"📎 Applying metadata filter: {filter_by}")
    
            retriever = vector_store.as_retriever(search_kwargs=search_kwargs)
            results = retriever.get_relevant_documents(query)
            logger.info(f"✅ Retrieved {len(results)} relevant documents")
            return results
        except Exception as e:
            logger.error(f"❌ Error retrieving relevant documents: {e}", exc_info=True)
            return []

