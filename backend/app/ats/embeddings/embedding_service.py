"""Deterministic embedding service with fixed model priority and finer similarity buckets."""
from __future__ import annotations

import numpy as np
from loguru import logger

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None  # type: ignore

PRIMARY_MODEL = "BAAI/bge-small-en-v1.5"
FALLBACK_MODEL = "all-MiniLM-L6-v2"


class EmbeddingService:
    """Lazy-loaded singleton embedding generator. Deterministic for same inputs."""

    _instance: "EmbeddingService | None" = None

    def __new__(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._model = None
            cls._instance._model_name = ""
        return cls._instance

    def _load(self) -> None:
        if self._model is not None:
            return
        if SentenceTransformer is None:
            logger.warning("sentence-transformers not installed; semantic scores will be 0")
            return
        for model_name in (PRIMARY_MODEL, FALLBACK_MODEL):
            try:
                logger.info(f"Loading embedding model: {model_name}")
                # self._model = SentenceTransformer(model_name)
                self._model = SentenceTransformer(
                    model_name,
                    cache_folder="/app/.cache/huggingface",
                )
                self._model_name = model_name
                return
            except Exception as exc:
                logger.warning(f"Failed to load {model_name}: {exc}")
        logger.error("No embedding model available")

    def encode(self, texts: list[str]) -> np.ndarray:
        """Return L2-normalized embeddings as numpy array shape (n, dim)."""
        if not texts:
            return np.zeros((0, 384))
        self._load()
        # if self._model is None:
        #     return np.zeros((len(texts), 384))
        if self._model is None:
            raise RuntimeError(
                "Embedding model could not be loaded. Semantic matching is unavailable."
            )
        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(embeddings, dtype=np.float64)

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        if a.size == 0 or b.size == 0:
            return 0.0
        return float(np.clip(np.dot(a, b), -1.0, 1.0))

    @staticmethod
    def similarity_to_bucket(similarity: float) -> float:
        """
        Map cosine similarity to a deterministic fine-grained bucket score (0–100).

        Thresholds reflect recruiter-quality matching expectations:
          ≥ 0.90 → 100 (near-perfect / synonym)
          ≥ 0.85 →  95 (very strong match)
          ≥ 0.80 →  88 (strong match)
          ≥ 0.75 →  80 (good match)
          ≥ 0.70 →  72 (solid match)
          ≥ 0.65 →  63 (partial match)
          ≥ 0.55 →  52 (weak/transferable)
          ≥ 0.45 →  38 (tangentially related)
          < 0.45 →   0 (no meaningful match)

        Using finer buckets eliminates the previous scoring cliff where a similarity
        of 0.89 mapped to 0 instead of receiving fair partial credit.
        """
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


# """
# Embedding service using local SentenceTransformer (recommended approach).

# Why local over HF remote API:
# - Remote API caused 10+ minute timeouts (655,183ms in logs)
# - Remote API has cold starts, rate limits, and no SLA on free tier
# - Local inference is ~50ms, deterministic, and always available
# - Railway 512MB+ plan easily handles bge-small-en-v1.5 (~130MB)
# """
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
#     """
#     Lazy-loaded singleton embedding generator.
#     Deterministic: same input always produces same output.
#     Thread-safe after first _load() call (Railway runs single worker).
#     """

#     _instance: "EmbeddingService | None" = None

#     def __new__(cls) -> "EmbeddingService":
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#             cls._instance._model = None
#             cls._instance._model_name = ""
#         return cls._instance

#     # ------------------------------------------------------------------
#     # Internal helpers
#     # ------------------------------------------------------------------

#     def _load(self) -> None:
#         """Load the embedding model once; subsequent calls are no-ops."""
#         if self._model is not None:
#             return

#         if SentenceTransformer is None:
#             logger.warning(
#                 "sentence-transformers not installed; "
#                 "semantic scores will be unavailable."
#             )
#             return

#         for model_name in (PRIMARY_MODEL, FALLBACK_MODEL):
#             try:
#                 logger.info(f"Loading embedding model: {model_name}")
#                 self._model = SentenceTransformer(
#                     model_name,
#                     cache_folder="/app/.cache/huggingface",
#                 )
#                 self._model_name = model_name
#                 logger.info(f"Embedding model loaded: {model_name}")
#                 return
#             except Exception as exc:
#                 logger.warning(f"Failed to load {model_name}: {exc}")

#         logger.error("No embedding model could be loaded.")

#     # ------------------------------------------------------------------
#     # Public API
#     # ------------------------------------------------------------------

#     def encode(self, texts: list[str]) -> np.ndarray:
#         """
#         Return L2-normalized embeddings as numpy array of shape (n, dim).

#         Raises:
#             RuntimeError: if no model is available (install sentence-transformers).
#         """
#         if not texts:
#             return np.zeros((0, 384))

#         self._load()

#         if self._model is None:
#             raise RuntimeError(
#                 "Embedding model could not be loaded. "
#                 "Ensure sentence-transformers is installed and "
#                 "Railway has at least 512MB of memory."
#             )

#         embeddings = self._model.encode(
#             texts,
#             convert_to_numpy=True,
#             normalize_embeddings=True,   # L2-normalize in one step
#             show_progress_bar=False,
#         )
#         return np.asarray(embeddings, dtype=np.float64)

#     @staticmethod
#     def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
#         """
#         Compute cosine similarity between two L2-normalized vectors.
#         Since vectors are already normalized, this is just the dot product.
#         Result is clipped to [-1, 1] to guard against floating-point drift.
#         """
#         if a.size == 0 or b.size == 0:
#             return 0.0
#         return float(np.clip(np.dot(a, b), -1.0, 1.0))

#     @staticmethod
#     def similarity_to_bucket(similarity: float) -> float:
#         """
#         Map cosine similarity → deterministic fine-grained bucket score (0–100).

#         Thresholds reflect recruiter-quality matching expectations:
#           ≥ 0.90 → 100  (near-perfect / synonym)
#           ≥ 0.85 →  95  (very strong match)
#           ≥ 0.80 →  88  (strong match)
#           ≥ 0.75 →  80  (good match)
#           ≥ 0.70 →  72  (solid match)
#           ≥ 0.65 →  63  (partial match)
#           ≥ 0.55 →  52  (weak / transferable)
#           ≥ 0.45 →  38  (tangentially related)
#           < 0.45 →   0  (no meaningful match)

#         Fine buckets eliminate the old scoring cliff where similarity=0.89
#         incorrectly mapped to 0 instead of receiving fair partial credit.
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


# # Module-level singleton — import this everywhere
# embedding_service = EmbeddingService()
