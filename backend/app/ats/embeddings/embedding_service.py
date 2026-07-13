# """Deterministic embedding service with fixed model priority and finer similarity buckets."""
# from __future__ import annotations

# import numpy as np
# from loguru import logger

# try:
#     from sentence_transformers import SentenceTransformer
# except ImportError:
#     SentenceTransformer = None  # type: ignore

# PRIMARY_MODEL = "BAAI/bge-small-en-v1.5"
# FALLBACK_MODEL = "all-MiniLM-L6-v2"


# class EmbeddingService:
#     """Lazy-loaded singleton embedding generator. Deterministic for same inputs."""

#     _instance: "EmbeddingService | None" = None

#     def __new__(cls) -> "EmbeddingService":
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#             cls._instance._model = None
#             cls._instance._model_name = ""
#         return cls._instance

#     def _load(self) -> None:
#         if self._model is not None:
#             return
#         if SentenceTransformer is None:
#             logger.warning("sentence-transformers not installed; semantic scores will be 0")
#             return
#         for model_name in (PRIMARY_MODEL, FALLBACK_MODEL):
#             try:
#                 logger.info(f"Loading embedding model: {model_name}")
#                 # self._model = SentenceTransformer(model_name)
#                 self._model = SentenceTransformer(
#                     model_name,
#                     cache_folder="/app/.cache/huggingface",
#                 )
#                 self._model_name = model_name
#                 return
#             except Exception as exc:
#                 logger.warning(f"Failed to load {model_name}: {exc}")
#         logger.error("No embedding model available")

#     def encode(self, texts: list[str]) -> np.ndarray:
#         """Return L2-normalized embeddings as numpy array shape (n, dim)."""
#         if not texts:
#             return np.zeros((0, 384))
#         self._load()
#         # if self._model is None:
#         #     return np.zeros((len(texts), 384))
#         if self._model is None:
#             raise RuntimeError(
#                 "Embedding model could not be loaded. Semantic matching is unavailable."
#             )
#         embeddings = self._model.encode(
#             texts,
#             convert_to_numpy=True,
#             normalize_embeddings=True,
#             show_progress_bar=False,
#         )
#         return np.asarray(embeddings, dtype=np.float64)

#     @staticmethod
#     def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
#         if a.size == 0 or b.size == 0:
#             return 0.0
#         return float(np.clip(np.dot(a, b), -1.0, 1.0))

#     @staticmethod
#     def similarity_to_bucket(similarity: float) -> float:
#         """
#         Map cosine similarity to a deterministic fine-grained bucket score (0–100).

#         Thresholds reflect recruiter-quality matching expectations:
#           ≥ 0.90 → 100 (near-perfect / synonym)
#           ≥ 0.85 →  95 (very strong match)
#           ≥ 0.80 →  88 (strong match)
#           ≥ 0.75 →  80 (good match)
#           ≥ 0.70 →  72 (solid match)
#           ≥ 0.65 →  63 (partial match)
#           ≥ 0.55 →  52 (weak/transferable)
#           ≥ 0.45 →  38 (tangentially related)
#           < 0.45 →   0 (no meaningful match)

#         Using finer buckets eliminates the previous scoring cliff where a similarity
#         of 0.89 mapped to 0 instead of receiving fair partial credit.
#         """
#         if similarity >= 0.90:
#             return 100.0
#         if similarity >= 0.85:
#             return 95.0
#         if similarity >= 0.80:
#             return 88.0
#         if similarity >= 0.75:
#             return 80.0
#         if similarity >= 0.70:
#             return 72.0
#         if similarity >= 0.65:
#             return 63.0
#         if similarity >= 0.55:
#             return 52.0
#         if similarity >= 0.45:
#             return 38.0
#         return 0.0


# embedding_service = EmbeddingService()
"""Deterministic embedding service using Hugging Face Free Inference API."""
from __future__ import annotations
import os
import numpy as np
from loguru import logger

from huggingface_hub import InferenceClient

PRIMARY_MODEL = "BAAI/bge-small-en-v1.5"
FALLBACK_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

class EmbeddingService:
    """Singleton embedding generator leveraging free remote inference."""
    _instance: "EmbeddingService | None" = None

    def __new__(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Fetch token from Railway environment variables
            token = os.getenv("HF_TOKEN")
            cls._instance._client = InferenceClient(token=token)
        return cls._instance

    def encode(self, texts: list[str]) -> np.ndarray:
        """Return L2-normalized embeddings via Serverless API."""
        if not texts:
            return np.zeros((0, 384))
        
        for model_name in (PRIMARY_MODEL, FALLBACK_MODEL):
            try:
                logger.info(f"Requesting embeddings from API: {model_name}")
                # Call Hugging Face API to extract features remotely
                response = self._client.feature_extraction(text=texts, model=model_name)
                embeddings = np.array(response, dtype=np.float64)
                
                # Manually L2-normalize the resulting vectors
                norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
                # Avoid division by zero
                norms = np.where(norms == 0, 1.0, norms)
                return embeddings / norms
                
            except Exception as exc:
                logger.warning(f"API failed for {model_name}: {exc}")
                
        raise RuntimeError("Both remote embedding models failed or rate-limited.")

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        if a.size == 0 or b.size == 0:
            return 0.0
        return float(np.clip(np.dot(a, b), -1.0, 1.0))

        @staticmethod
        def similarity_to_bucket(similarity: float) -> float:
            if similarity >= 0.90:
                return 100.0
            if similarity >= 0.85:
                return 95.0
            if similarity >= 0.80:
                return 88.0
            if similarity >= 0.75:
                return 80.0
            if similarity >= 0.70:
                return 72.0
            if similarity >= 0.65:
                return 63.0
            if similarity >= 0.55: 
                return 52.0
            if similarity >= 0.45:
                return 38.0
            return 0.0
embedding_service = EmbeddingService()
