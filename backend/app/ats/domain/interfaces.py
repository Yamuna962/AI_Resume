"""Abstract interfaces for ATS engine components (SOLID / dependency inversion)."""
from abc import ABC, abstractmethod

from app.ats.domain.schemas import (
    ATSBreakdown,
    DetailedScoreBreakdown,
    FormattingResult,
    FusionResult,
    KeywordMatchResult,
    LLMExplanation,
    MatchScoreResult,
    ParsedJobDescription,
    ParsedResume,
    SemanticMatchResult,
    EducationMatchResult,
    ExperienceMatchResult,
    ProjectMatchResult,
)


class IResumeParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> ParsedResume: ...


class IJobDescriptionParser(ABC):
    @abstractmethod
    def parse(self, text: str) -> ParsedJobDescription: ...


class ISkillNormalizer(ABC):
    @abstractmethod
    def normalize_resume(self, resume: ParsedResume) -> ParsedResume: ...

    @abstractmethod
    def normalize_jd(self, jd: ParsedJobDescription) -> ParsedJobDescription: ...


class IKeywordMatcher(ABC):
    @abstractmethod
    def match(
        self, resume: ParsedResume, jd: ParsedJobDescription
    ) -> KeywordMatchResult: ...


class ISemanticMatcher(ABC):
    @abstractmethod
    def match(
        self, resume: ParsedResume, jd: ParsedJobDescription
    ) -> SemanticMatchResult: ...


class IExperienceMatcher(ABC):
    @abstractmethod
    def match(
        self, resume: ParsedResume, jd: ParsedJobDescription
    ) -> ExperienceMatchResult: ...


class IProjectMatcher(ABC):
    @abstractmethod
    def match(
        self, resume: ParsedResume, jd: ParsedJobDescription
    ) -> ProjectMatchResult: ...


class IEducationMatcher(ABC):
    @abstractmethod
    def match(
        self, resume: ParsedResume, jd: ParsedJobDescription
    ) -> EducationMatchResult: ...


class IFormattingAnalyzer(ABC):
    @abstractmethod
    def analyze(self, resume: ParsedResume) -> FormattingResult: ...


class IATSFusionEngine(ABC):
    @abstractmethod
    def fuse(
        self,
        keyword: KeywordMatchResult,
        semantic: SemanticMatchResult,
        experience: ExperienceMatchResult,
        projects: ProjectMatchResult,
        formatting: FormattingResult,
        education: EducationMatchResult,
    ) -> FusionResult: ...


class IMatchScoreEngine(ABC):
    @abstractmethod
    def calculate(
        self,
        keyword: KeywordMatchResult,
        semantic: SemanticMatchResult,
        experience: ExperienceMatchResult,
        projects: ProjectMatchResult,
        jd: ParsedJobDescription,
    ) -> MatchScoreResult: ...


class ILLMExplanationEngine(ABC):
    @abstractmethod
    async def explain(
        self,
        resume: ParsedResume,
        jd: ParsedJobDescription,
        ats_score: int,
        match_score: int,
        breakdown: ATSBreakdown,
        keyword: KeywordMatchResult,
        semantic: SemanticMatchResult,
        experience: ExperienceMatchResult,
        projects: ProjectMatchResult,
        formatting: FormattingResult,
        detailed_scores: DetailedScoreBreakdown | None = None,
        pre_strengths: list[str] | None = None,
        pre_weaknesses: list[str] | None = None,
        transferable_skills: list[str] | None = None,
    ) -> LLMExplanation: ...
