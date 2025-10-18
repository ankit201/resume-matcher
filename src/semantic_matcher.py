"""
Semantic Matching Engine
Fast first-pass filtering using sentence embeddings and cosine similarity.
Provides semantic understanding beyond keyword matching.

Now integrated with ChromaDB for efficient vector storage and retrieval.
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache

from .models import ParsedResume, ParsedJobDescription, SkillMatch
from .vector_store import ResumeVectorStore
from config.settings import get_settings


class SemanticMatcher:
    """
    Semantic matching using sentence transformers.
    Provides fast, context-aware similarity scoring.
    Integrated with ChromaDB vector store for efficient retrieval.
    """
    
    def __init__(
        self, 
        model_name: Optional[str] = None,
        use_vector_store: bool = True,
        vector_store_path: Optional[str] = None
    ):
        """
        Initialize semantic matcher with embedding model.
        
        Args:
            model_name: SentenceTransformer model name (default from settings)
            use_vector_store: Whether to use ChromaDB for storage/retrieval
            vector_store_path: Path to ChromaDB persistence directory
        """
        settings = get_settings()
        self.model_name = model_name or settings.embedding_model
        self.model = self._load_model()
        self.threshold = settings.semantic_threshold
        
        # Initialize vector store if enabled
        self.use_vector_store = use_vector_store
        self.vector_store = None
        if use_vector_store:
            store_path = vector_store_path or getattr(settings, 'vector_store_path', './data/vector_store')
            self.vector_store = ResumeVectorStore(persist_directory=store_path)
    
    @lru_cache(maxsize=1)
    def _load_model(self) -> SentenceTransformer:
        """Load and cache the embedding model"""
        return SentenceTransformer(self.model_name)
    
    def compute_overall_similarity(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> float:
        """
        Compute overall semantic similarity between resume and JD using bi-encoder.
        
        Args:
            resume: Parsed resume
            job_description: Parsed job description
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Create comprehensive text representations
        resume_text = self._create_resume_representation(resume)
        jd_text = self._create_jd_representation(job_description)
        
        # Generate embeddings
        embeddings = self.model.encode([resume_text, jd_text])
        
        # Calculate cosine similarity (reshape to 2D arrays)
        similarity = cosine_similarity(
            embeddings[0].reshape(1, -1), 
            embeddings[1].reshape(1, -1)
        )[0][0]
        
        return float(similarity)
    
    def compute_skills_match(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> List[SkillMatch]:
        """
        Detailed skills matching with semantic understanding.
        
        Args:
            resume: Parsed resume
            job_description: Parsed job description
        
        Returns:
            List of SkillMatch objects with details
        """
        if not resume.skills:
            return []
        
        # Combine required and preferred skills
        all_jd_skills = job_description.required_skills + job_description.preferred_skills
        
        if not all_jd_skills:
            return []
        
        # Generate embeddings for all skills
        resume_skills_embeddings = self.model.encode(resume.skills)
        jd_skills_embeddings = self.model.encode(all_jd_skills)
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(jd_skills_embeddings, resume_skills_embeddings)
        
        # Analyze each JD skill
        skill_matches = []
        
        for idx, jd_skill in enumerate(all_jd_skills):
            similarities = similarity_matrix[idx]
            max_similarity_idx = np.argmax(similarities)
            max_similarity = similarities[max_similarity_idx]
            
            if max_similarity >= 0.9:  # Very high similarity - exact match
                match_type = "exact"
            elif max_similarity >= self.threshold:  # Above threshold - similar
                match_type = "similar"
            else:
                match_type = "missing"
            
            is_required = jd_skill in job_description.required_skills
            
            skill_match = SkillMatch(
                skill=jd_skill,
                match_type=match_type,
                relevance_score=float(max_similarity),
                explanation=(
                    f"Matches '{resume.skills[max_similarity_idx]}'" 
                    if match_type in ["exact", "similar"] 
                    else "Not found in resume"
                )
            )
            
            skill_matches.append(skill_match)
        
        return skill_matches
    
    def compute_experience_relevance(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> Dict[str, float]:
        """
        Calculate relevance of work experience to job requirements.
        
        Args:
            resume: Parsed resume
            job_description: Parsed job description
        
        Returns:
            Dictionary with relevance metrics
        """
        if not resume.work_experience:
            return {
                "overall_relevance": 0.0,
                "most_relevant_role_score": 0.0,
                "average_relevance": 0.0
            }
        
        # Create JD requirements text
        jd_requirements = " ".join([
            job_description.summary,
            " ".join(job_description.responsibilities),
            " ".join(job_description.required_skills)
        ])
        
        # Encode JD requirements once
        jd_embedding = self.model.encode([jd_requirements])[0]
        
        # Calculate relevance for each experience
        relevance_scores = []
        
        for exp in resume.work_experience:
            # Create experience text
            exp_text = f"{exp.title} at {exp.company}. {exp.description}"
            if exp.achievements:
                exp_text += " " + " ".join(exp.achievements)
            if exp.technologies:
                exp_text += " Technologies: " + ", ".join(exp.technologies)
            
            # Calculate similarity
            exp_embedding = self.model.encode([exp_text])[0]
            similarity = cosine_similarity(
                jd_embedding.reshape(1, -1), 
                exp_embedding.reshape(1, -1)
            )[0][0]
            relevance_scores.append(float(similarity))
        
        return {
            "overall_relevance": float(np.max(relevance_scores)),
            "most_relevant_role_score": float(np.max(relevance_scores)),
            "average_relevance": float(np.mean(relevance_scores)),
            "top_3_average": float(np.mean(sorted(relevance_scores, reverse=True)[:3]))
        }
    
    def compute_section_similarities(
        self,
        resume: ParsedResume,
        job_description: ParsedJobDescription
    ) -> Dict[str, float]:
        """
        Compute similarity for different resume sections vs JD.
        
        Args:
            resume: Parsed resume
            job_description: Parsed job description
        
        Returns:
            Dictionary with section-wise similarities
        """
        jd_text = self._create_jd_representation(job_description)
        jd_embedding = self.model.encode([jd_text])[0]
        
        results = {}
        
        # Skills similarity
        if resume.skills:
            skills_text = ", ".join(resume.skills)
            skills_emb = self.model.encode([skills_text])[0]
            results["skills_similarity"] = float(
                cosine_similarity(
                    jd_embedding.reshape(1, -1), 
                    skills_emb.reshape(1, -1)
                )[0][0]
            )
        else:
            results["skills_similarity"] = 0.0
        
        # Experience similarity
        if resume.work_experience:
            exp_text = " ".join([
                f"{e.title}: {e.description}" for e in resume.work_experience
            ])
            exp_emb = self.model.encode([exp_text])[0]
            results["experience_similarity"] = float(
                cosine_similarity(
                    jd_embedding.reshape(1, -1), 
                    exp_emb.reshape(1, -1)
                )[0][0]
            )
        else:
            results["experience_similarity"] = 0.0
        
        # Education similarity
        if resume.education:
            edu_text = " ".join([
                f"{e.degree} in {e.field_of_study or ''} from {e.institution}"
                for e in resume.education
            ])
            edu_emb = self.model.encode([edu_text])[0]
            results["education_similarity"] = float(
                cosine_similarity(
                    jd_embedding.reshape(1, -1), 
                    edu_emb.reshape(1, -1)
                )[0][0]
            )
        else:
            results["education_similarity"] = 0.0
        
        # Summary similarity
        if resume.summary:
            summary_emb = self.model.encode([resume.summary])[0]
            results["summary_similarity"] = float(
                cosine_similarity(
                    jd_embedding.reshape(1, -1), 
                    summary_emb.reshape(1, -1)
                )[0][0]
            )
        else:
            results["summary_similarity"] = 0.0
        
        return results
    
    def _create_resume_representation(self, resume: ParsedResume) -> str:
        """Create comprehensive text representation of resume"""
        parts = []
        
        if resume.summary:
            parts.append(f"Professional Summary: {resume.summary}")
        
        if resume.skills:
            parts.append(f"Skills: {', '.join(resume.skills)}")
        
        if resume.work_experience:
            for exp in resume.work_experience:
                exp_text = f"{exp.title} at {exp.company}. {exp.description}"
                if exp.technologies:
                    exp_text += f" Technologies: {', '.join(exp.technologies)}"
                parts.append(exp_text)
        
        if resume.education:
            for edu in resume.education:
                parts.append(
                    f"{edu.degree} in {edu.field_of_study or 'N/A'} from {edu.institution}"
                )
        
        if resume.certifications:
            certs = [f"{c.name} from {c.issuer}" for c in resume.certifications]
            parts.append(f"Certifications: {', '.join(certs)}")
        
        return " ".join(parts)
    
    def _create_jd_representation(self, jd: ParsedJobDescription) -> str:
        """Create comprehensive text representation of job description"""
        parts = [
            f"Job Title: {jd.job_title}",
            f"Summary: {jd.summary}"
        ]
        
        if jd.responsibilities:
            parts.append(f"Responsibilities: {' '.join(jd.responsibilities)}")
        
        if jd.required_skills:
            parts.append(f"Required Skills: {', '.join(jd.required_skills)}")
        
        if jd.preferred_skills:
            parts.append(f"Preferred Skills: {', '.join(jd.preferred_skills)}")
        
        if jd.education_requirements:
            parts.append(f"Education: {' '.join(jd.education_requirements)}")
        
        return " ".join(parts)
    
    def batch_compute_similarities(
        self,
        resumes: List[ParsedResume],
        job_description: ParsedJobDescription
    ) -> List[Tuple[int, float]]:
        """
        Compute similarities for multiple resumes efficiently using bi-encoder.
        
        Args:
            resumes: List of parsed resumes
            job_description: Job description to match against
        
        Returns:
            List of (index, similarity_score) tuples, sorted by score descending
        """
        resume_texts = [self._create_resume_representation(r) for r in resumes]
        jd_text = self._create_jd_representation(job_description)
        
        # Batch encode (more efficient)
        all_texts = resume_texts + [jd_text]
        embeddings = self.model.encode(all_texts)
        
        # JD embedding is the last one
        jd_embedding = embeddings[-1]
        resume_embeddings = embeddings[:-1]
        
        # Calculate similarities (reshape jd_embedding to 2D)
        similarities = cosine_similarity(jd_embedding.reshape(1, -1), resume_embeddings)[0]
        
        # Create (index, score) pairs and sort
        results = [(i, float(score)) for i, score in enumerate(similarities)]
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    # ========== Vector Store Integration Methods ==========
    
    def add_resume_to_store(
        self,
        resume: ParsedResume,
        resume_id: Optional[str] = None
    ) -> str:
        """
        Add a resume to the vector store for efficient retrieval.
        
        Args:
            resume: Parsed resume to add
            resume_id: Optional resume ID (auto-generated if not provided)
        
        Returns:
            Resume ID in the vector store
        """
        if not self.use_vector_store or self.vector_store is None:
            raise RuntimeError("Vector store is not enabled")
        
        resume_text = self._create_resume_representation(resume)
        
        # Use email as identifier, or "Unknown"
        name = "Unknown"
        if resume.contact_info and resume.contact_info.email:
            name = resume.contact_info.email.split('@')[0] if resume.contact_info.email else "Unknown"
        
        metadata = {
            "name": name,
            "email": getattr(resume.contact_info, "email", "") if resume.contact_info else "",
            "skills": ", ".join(resume.skills) if resume.skills else "",
            "total_experience_years": len(resume.work_experience) if resume.work_experience else 0
        }
        
        # Auto-generate ID if not provided
        if not resume_id:
            import uuid
            resume_id = str(uuid.uuid4())
        
        self.vector_store.add_resume(
            resume_id=resume_id,
            resume_text=resume_text,
            metadata=metadata
        )
        return resume_id
    
    def add_resumes_batch_to_store(
        self,
        resumes: List[ParsedResume],
        resume_ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add multiple resumes to the vector store in batch.
        
        Args:
            resumes: List of parsed resumes
            resume_ids: Optional list of resume IDs
        
        Returns:
            List of resume IDs in the vector store
        """
        if not self.use_vector_store or self.vector_store is None:
            raise RuntimeError("Vector store is not enabled")
        
        resume_texts = [self._create_resume_representation(r) for r in resumes]
        
        metadata_list = []
        for resume in resumes:
            # Use email as identifier, or "Unknown"
            name = "Unknown"
            if resume.contact_info and resume.contact_info.email:
                name = resume.contact_info.email.split('@')[0] if resume.contact_info.email else "Unknown"
            
            metadata = {
                "name": name,
                "email": getattr(resume.contact_info, "email", "") if resume.contact_info else "",
                "skills": ", ".join(resume.skills) if resume.skills else "",
                "total_experience_years": len(resume.work_experience) if resume.work_experience else 0
            }
            metadata_list.append(metadata)
        
        # Auto-generate IDs if not provided
        if not resume_ids:
            import uuid
            resume_ids = [str(uuid.uuid4()) for _ in resumes]
        
        self.vector_store.add_resumes_batch(
            resume_ids=resume_ids,
            resume_texts=resume_texts,
            metadatas=metadata_list
        )
        return resume_ids
    
    def search_candidates_by_jd(
        self,
        job_description: ParsedJobDescription,
        top_k: int = 10,
        min_score: float = 0.7
    ) -> List[Dict]:
        """
        Search for best matching candidates using vector store.
        
        Args:
            job_description: Job description to match against
            top_k: Number of top candidates to return
            min_score: Minimum similarity threshold
        
        Returns:
            List of candidate dictionaries with resume_id, score, and metadata
        """
        if not self.use_vector_store or self.vector_store is None:
            raise RuntimeError("Vector store is not enabled")
        
        jd_text = self._create_jd_representation(job_description)
        
        # Fast vector search
        candidates = self.vector_store.search_by_job_description(
            job_description_text=jd_text,
            n_results=top_k,
            threshold=min_score
        )
        
        return candidates
    
    def search_similar_candidates(
        self,
        reference_resume: ParsedResume,
        top_k: int = 5,
        min_score: float = 0.8
    ) -> List[Dict]:
        """
        Find candidates similar to a reference resume.
        
        Args:
            reference_resume: Reference resume to match against
            top_k: Number of similar candidates to return
            min_score: Minimum similarity threshold
        
        Returns:
            List of similar candidate dictionaries
        """
        if not self.use_vector_store or self.vector_store is None:
            raise RuntimeError("Vector store is not enabled")
        
        resume_text = self._create_resume_representation(reference_resume)
        
        return self.vector_store.search_similar_resumes(
            query_text=resume_text,
            n_results=top_k,
            min_similarity=min_score
        )
