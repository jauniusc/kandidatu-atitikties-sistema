from dataclasses import dataclass

from app.domain.models import Candidate, Criterion


@dataclass
class SkillCriterion(Criterion):
    skill: str
    required_level: int
    weight: float

    def name(self) -> str:
        return self.skill

    def description(self) -> str:
        return f"{self.skill}: reikalaujamas lygis {self.required_level}"

    def score(self, candidate: Candidate) -> float | None:
        level = candidate.skills.get(self.skill)
        if level is None:
            return None
        return min(level / self.required_level, 1.0) * 100


@dataclass
class ExperienceCriterion(Criterion):
    min_years: float
    weight: float

    def name(self) -> str:
        return "patirtis"

    def description(self) -> str:
        return f"Patirtis: bent {self.min_years} m."

    def score(self, candidate: Candidate) -> float | None:
        if candidate.experience_years is None:
            return None
        return min(candidate.experience_years / self.min_years, 1.0) * 100


@dataclass
class SalaryCriterion(Criterion):
    min_salary: float
    max_salary: float
    weight: float

    def name(self) -> str:
        return "atlyginimas"

    def description(self) -> str:
        return f"Atlyginimas: {self.min_salary}–{self.max_salary}"

    def score(self, candidate: Candidate) -> float | None:
        expectation = candidate.salary_expectation
        if expectation is None:
            return None
        if expectation <= self.max_salary:
            return 100.0
        allowed_excess = 0.1 * self.max_salary
        if expectation <= self.max_salary + allowed_excess:
            return (1 - (expectation - self.max_salary) / allowed_excess) * 100
        return 0.0


def create_criterion(data: dict) -> Criterion:
    if data["type"] == "skill":
        return SkillCriterion(skill=data["skill"], required_level=data["required_level"], weight=data["weight"])
    if data["type"] == "experience":
        return ExperienceCriterion(min_years=data["min_years"], weight=data["weight"])
    if data["type"] == "salary":
        return SalaryCriterion(
            min_salary=data["min_salary"], max_salary=data["max_salary"], weight=data["weight"]
        )
