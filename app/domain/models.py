from abc import ABC, abstractmethod
from dataclasses import dataclass

SUITABLE = "TINKAMAS"
NOT_SUITABLE = "NETINKAMAS"
MANUAL_REVIEW = "PERŽIŪRĖTI RANKINIU BŪDU"
UNKNOWN = "nežinoma"


@dataclass
class Candidate:
    name: str
    skills: dict[str, int]
    experience_years: float | None = None
    salary_expectation: float | None = None


class Criterion(ABC):
    weight: float

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def score(self, candidate: Candidate) -> float | None:
        pass


@dataclass
class Position:
    id: int
    title: str
    required_skills: list[str]
    criteria: list[Criterion]


@dataclass
class Evaluation:
    score: float | None
    recommendation: str
    explanation: dict
    note: str
