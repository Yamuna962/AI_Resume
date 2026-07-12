try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

import numpy as np


class EmbeddingGenerator:
    def __init__(self):
        self.model = None

    def _load_model(self):
        if self.model is None and SentenceTransformer is not None:
            # We use all-MiniLM-L6-v2 which outputs a 384-dimensional vector
            self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def generate(self, texts: list[str]) -> list[list[float]]:
        """Generates embeddings for a list of strings."""
        if not texts:
            return []
            
        if SentenceTransformer is None:
            # Fallback for dev/testing without torch installed
            return [[0.0] * 384 for _ in texts]
            
        self._load_model()
        if self.model:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        return [[0.0] * 384 for _ in texts]

    def chunk_resume(self, resume_sections: dict[str, str]) -> list[dict[str, str]]:
        """
        Converts the parsed resume sections into chunks suitable for embedding.
        """
        chunks = []
        for section_type, content in resume_sections.items():
            if not content.strip():
                continue
                
            # If a section is very long, we should chunk it further by paragraphs
            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
            for p in paragraphs:
                chunks.append({
                    "chunk_text": p,
                    "chunk_type": section_type
                })
                
        return chunks


embedding_generator = EmbeddingGenerator()
