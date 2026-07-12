from pydantic import BaseModel

try:
    from sentence_transformers import CrossEncoder
except ImportError:
    CrossEncoder = None


class SemanticMatchResult(BaseModel):
    matched: list[dict[str, str | float]]
    missing: list[str]
    score: float


class SemanticMatcher:
    def __init__(self):
        # We will lazy-load the model to avoid huge memory usage on startup if not needed immediately
        self.model = None

    def _load_model(self):
        if self.model is None and CrossEncoder is not None:
            # We use a paraphrase cross-encoder to detect synonyms
            self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def match(self, resume_skills: list[str], jd_skills: list[str]) -> SemanticMatchResult:
        """
        Performs semantic matching using a cross-encoder to find synonyms (e.g. k8s <-> Kubernetes).
        """
        if not jd_skills:
            return SemanticMatchResult(matched=[], missing=[], score=100.0)
        
        if not resume_skills:
            return SemanticMatchResult(matched=[], missing=jd_skills, score=0.0)

        # Fallback if sentence-transformers not installed (e.g., during testing or light mode)
        if CrossEncoder is None:
            return SemanticMatchResult(matched=[], missing=jd_skills, score=0.0)

        self._load_model()

        matched_list = []
        missing_list = set(jd_skills)
        
        # Build pairs
        pairs = []
        pair_mapping = []  # To keep track of which score belongs to which (jd_skill, res_skill)
        
        for jd_skill in jd_skills:
            for res_skill in resume_skills:
                pairs.append((jd_skill, res_skill))
                pair_mapping.append((jd_skill, res_skill))
                
        # Predict similarity scores for all pairs at once
        if self.model:
            scores = self.model.predict(pairs)
        else:
            scores = [0.0] * len(pairs)
            
        # Analyze results
        # Threshold for ms-marco model is typically > 0 (it outputs logits)
        threshold = 2.0 
        
        for i, score in enumerate(scores):
            jd_skill, res_skill = pair_mapping[i]
            
            if score > threshold:
                matched_list.append({
                    "resume_skill": res_skill,
                    "jd_skill": jd_skill,
                    "score": float(score)
                })
                missing_list.discard(jd_skill)

        score_val = ((len(jd_skills) - len(missing_list)) / len(jd_skills)) * 100.0 if jd_skills else 100.0

        return SemanticMatchResult(
            matched=matched_list,
            missing=list(missing_list),
            score=round(score_val, 2),
        )


semantic_matcher = SemanticMatcher()
