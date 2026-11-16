import pytest

from app.domain.criteria import ExperienceCriterion, SalaryCriterion, SkillCriterion
from app.domain.engine import InvalidWeightsError, evaluate
from app.domain.models import MANUAL_REVIEW, NOT_SUITABLE, SUITABLE, UNKNOWN, Candidate, Position


def developer_position() -> Position:
    return Position(
        id=1,
        title="Python programuotojas",
        required_skills=["Python"],
        criteria=[
            SkillCriterion(skill="SQL", required_level=3, weight=0.3),
            SkillCriterion(skill="Docker", required_level=2, weight=0.2),
            ExperienceCriterion(min_years=3, weight=0.3),
            SalaryCriterion(min_salary=2000, max_salary=2800, weight=0.2),
        ],
    )


def test_typical_candidate_is_suitable():
    candidate = Candidate(
        "Jonas", {"Python": 3, "SQL": 2, "Docker": 2}, experience_years=4, salary_expectation=2500
    )

    evaluation = evaluate(candidate, developer_position())

    assert evaluation.score == 90.0
    assert evaluation.recommendation == SUITABLE
    assert evaluation.explanation == {"SQL": 67, "Docker": 100, "patirtis": 100, "atlyginimas": 100}


def test_borderline_score_with_unknown_skill_goes_to_manual_review():
    candidate = Candidate("Ona", {"Python": 3, "SQL": 1}, experience_years=4, salary_expectation=2500)

    evaluation = evaluate(candidate, developer_position())

    assert evaluation.score == 60.0
    assert evaluation.recommendation == MANUAL_REVIEW
    assert evaluation.explanation == {"SQL": 33, "Docker": UNKNOWN, "patirtis": 100, "atlyginimas": 100}


def test_missing_required_skill_is_not_suitable_without_score():
    candidate = Candidate("Petras", {"SQL": 5, "Docker": 5}, experience_years=10, salary_expectation=2000)

    evaluation = evaluate(candidate, developer_position())

    assert evaluation.recommendation == NOT_SUITABLE
    assert evaluation.score is None


def test_weights_not_summing_to_one_raise_error():
    position = Position(
        id=3,
        title="Neteisingi svoriai",
        required_skills=[],
        criteria=[
            SkillCriterion(skill="SQL", required_level=3, weight=0.5),
            ExperienceCriterion(min_years=3, weight=0.4),
        ],
    )
    candidate = Candidate("Jonas", {"SQL": 3}, experience_years=4)

    with pytest.raises(InvalidWeightsError):
        evaluate(candidate, position)
