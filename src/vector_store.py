"""
Vector Store for Resume Semantic Search using ChromaDB
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ResumeVectorStore:
    """Vector store for resume semantic search using ChromaDB."""
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "resumes"
    ):
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False, allow_reset=True)
        )
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Initialized vector store: {collection_name}, Count: {self.collection.count()}")
    
    def add_resume(
        self,
        resume_id: str,
        resume_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add or update a resume in the vector store."""
        try:
            self.collection.upsert(
                documents=[resume_text],
                ids=[resume_id],
                metadatas=[metadata or {}]
            )
            logger.info(f"Added resume: {resume_id}")
        except Exception as e:
            logger.error(f"Failed to add resume {resume_id}: {e}")
            raise
    
    def add_resumes_batch(
        self,
        resume_ids: List[str],
        resume_texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Add multiple resumes in batch."""
        try:
            # Ensure metadatas is the correct type or None
            meta_list = metadatas if metadatas is not None else None
            self.collection.upsert(
                documents=resume_texts,
                ids=resume_ids,
                metadatas=meta_list  # type: ignore
            )
            logger.info(f"Added {len(resume_ids)} resumes in batch")
        except Exception as e:
            logger.error(f"Batch add failed: {e}")
            raise
    
    def search_similar_resumes(
        self,
        query_text: str,
        n_results: int = 10,
        filter_metadata: Optional[Dict] = None,
        min_similarity: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Search for similar resumes using semantic similarity."""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=filter_metadata,
                include=["documents", "metadatas", "distances"]
            )
            
            matches = []
            if results['ids'] and results['distances'] and results['documents'] and results['metadatas']:
                for i, resume_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    similarity = 1 - distance
                    
                    if similarity >= min_similarity:
                        matches.append({
                            'resume_id': resume_id,
                            'similarity': float(similarity),
                            'document': results['documents'][0][i],
                            'metadata': results['metadatas'][0][i]
                        })
            
            logger.info(f"Found {len(matches)} similar resumes")
            return matches
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def search_by_job_description(
        self,
        job_description_text: str,
        threshold: float = 0.7,
        n_results: int = 50,
        required_skills: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Find matching candidates for a job description."""
        filter_dict = None
        if required_skills:
            filter_dict = {
                "$or": [{"skills": {"$contains": skill}} for skill in required_skills]
            }
        
        matches = self.search_similar_resumes(
            query_text=job_description_text,
            n_results=n_results,
            filter_metadata=filter_dict,
            min_similarity=threshold
        )
        
        return matches
    
    def get_resume(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific resume by ID."""
        try:
            result = self.collection.get(
                ids=[resume_id],
                include=["documents", "metadatas"]
            )
            
            if result['ids'] and result['documents'] and result['metadatas']:
                return {
                    'resume_id': result['ids'][0],
                    'document': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
            return None
            
        except Exception as e:
            logger.error(f"Get resume failed: {e}")
            return None
    
    def delete_resume(self, resume_id: str) -> None:
        """Delete a resume from the store."""
        try:
            self.collection.delete(ids=[resume_id])
            logger.info(f"Deleted resume: {resume_id}")
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            raise
    
    def count(self) -> int:
        """Get total number of resumes in store."""
        return self.collection.count()
    
    def reset(self) -> None:
        """Clear all data."""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.warning("Vector store has been reset")
