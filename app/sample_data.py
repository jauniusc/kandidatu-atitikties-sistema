from app.domain.engine import evaluate
from app.domain.models import Candidate
from app.storage import Storage


def load_sample_data(storage: Storage) -> None:
    if storage.get_organizations():
        return

    code_workshop = storage.add_organization("UAB Kodo Dirbtuvės")
    data_house = storage.add_organization("UAB Duomenų Namai")

    developer = storage.add_position(
        code_workshop,
        "Python programuotojas",
        required_skills=["Python"],
        criteria=[
            {"type": "skill", "skill": "SQL", "required_level": 3, "weight": 0.3},
            {"type": "skill", "skill": "Docker", "required_level": 2, "weight": 0.2},
            {"type": "experience", "min_years": 3, "weight": 0.3},
            {"type": "salary", "min_salary": 2000, "max_salary": 2800, "weight": 0.2},
        ],
    )
    storage.add_position(
        code_workshop,
        "Testuotojas (klaidos pavyzdys: svoriai nesusumuoja į 1,0)",
        required_skills=[],
        criteria=[
            {"type": "skill", "skill": "Testavimas", "required_level": 3, "weight": 0.5},
            {"type": "experience", "min_years": 2, "weight": 0.4},
        ],
    )
    analyst = storage.add_position(
        data_house,
        "Duomenų analitikas",
        required_skills=["SQL"],
        criteria=[
            {"type": "skill", "skill": "Excel", "required_level": 3, "weight": 0.2},
            {"type": "skill", "skill": "Python", "required_level": 2, "weight": 0.2},
            {"type": "experience", "min_years": 2, "weight": 0.3},
            {"type": "salary", "min_salary": 1500, "max_salary": 2200, "weight": 0.3},
        ],
    )

    add_candidate(
        storage,
        code_workshop,
        developer,
        Candidate("Ona Onaitė", {"Python": 3, "SQL": 1}, experience_years=4, salary_expectation=2500),
    )
    add_candidate(
        storage,
        code_workshop,
        developer,
        Candidate("Petras Petraitis", {"SQL": 4, "Docker": 3}, experience_years=6, salary_expectation=2400),
    )
    add_candidate(
        storage,
        data_house,
        analyst,
        Candidate(
            "Rasa Rasaitė",
            {"SQL": 4, "Excel": 3, "Python": 1},
            experience_years=3,
            salary_expectation=2300,
        ),
    )


def add_candidate(storage: Storage, organization_id: int, position_id: int, candidate: Candidate) -> None:
    position = storage.get_position(organization_id, position_id)
    storage.add_candidate(organization_id, position_id, candidate, evaluate(candidate, position))
