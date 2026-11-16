from app.domain.models import (
    MANUAL_REVIEW,
    NOT_SUITABLE,
    SUITABLE,
    UNKNOWN,
    Candidate,
    Evaluation,
    Position,
)

REVIEW_ZONE_MIN = 50
REVIEW_ZONE_MAX = 65


class InvalidWeightsError(Exception):
    pass


def evaluate(candidate: Candidate, position: Position) -> Evaluation:
    check_weights(position)

    missing_skills = [skill for skill in position.required_skills if skill not in candidate.skills]
    if missing_skills:
        note = "Netenkinti privalomi reikalavimai: " + ", ".join(missing_skills)
        return Evaluation(score=None, recommendation=NOT_SUITABLE, explanation={}, note=note)

    score = 0.0
    explanation = {}
    unknown_criteria = []
    for criterion in position.criteria:
        percent = criterion.score(candidate)
        if percent is None:
            unknown_criteria.append(criterion.name())
            explanation[criterion.name()] = UNKNOWN
        else:
            score += percent * criterion.weight
            explanation[criterion.name()] = round(percent)
    score = round(score, 2)

    recommendation, note = decide(score, unknown_criteria)
    return Evaluation(score, recommendation, explanation, note)


def check_weights(position: Position) -> None:
    total = sum(criterion.weight for criterion in position.criteria)
    if abs(total - 1.0) > 0.000001:
        raise InvalidWeightsError("Neteisingi pozicijos svoriai")


def decide(score: float, unknown_criteria: list[str]) -> tuple[str, str]:
    if unknown_criteria:
        return MANUAL_REVIEW, "Trūksta duomenų: " + ", ".join(unknown_criteria)
    if REVIEW_ZONE_MIN <= score <= REVIEW_ZONE_MAX:
        return MANUAL_REVIEW, f"Balas ribinėje zonoje ({REVIEW_ZONE_MIN}–{REVIEW_ZONE_MAX})"
    if score > REVIEW_ZONE_MAX:
        return SUITABLE, ""
    return NOT_SUITABLE, ""
