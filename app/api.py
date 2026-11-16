from dataclasses import asdict
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.domain.criteria import SkillCriterion
from app.domain.engine import InvalidWeightsError, evaluate
from app.domain.models import Candidate, Position
from app.storage import Storage

INDEX_FILE = Path(__file__).parent / "static" / "index.html"


class CandidateInput(BaseModel):
    name: str
    skills: dict[str, int] = {}
    experience_years: float | None = None
    salary_expectation: float | None = None


def create_app(storage: Storage) -> FastAPI:
    app = FastAPI(title="Kandidatų atitikties vertinimo sistema")

    def current_organization(x_organization: int = Header()) -> int:
        if not storage.organization_exists(x_organization):
            raise HTTPException(status_code=404, detail="Organizacija nerasta")
        return x_organization

    def find_position(organization_id: int, position_id: int) -> Position:
        position = storage.get_position(organization_id, position_id)
        if position is None:
            raise HTTPException(status_code=404, detail="Pozicija nerasta")
        return position

    @app.get("/")
    def index():
        return FileResponse(INDEX_FILE)

    @app.get("/api/organizations")
    def list_organizations():
        return storage.get_organizations()

    @app.get("/api/positions")
    def list_positions(organization_id: int = Depends(current_organization)):
        return [position_to_json(position) for position in storage.get_positions(organization_id)]

    @app.post("/api/positions/{position_id}/candidates")
    def submit_candidate(
        position_id: int,
        data: CandidateInput,
        organization_id: int = Depends(current_organization),
    ):
        position = find_position(organization_id, position_id)
        candidate = Candidate(
            name=data.name,
            skills=data.skills,
            experience_years=data.experience_years,
            salary_expectation=data.salary_expectation,
        )
        try:
            evaluation = evaluate(candidate, position)
        except InvalidWeightsError as error:
            raise HTTPException(status_code=400, detail=str(error))
        storage.add_candidate(organization_id, position_id, candidate, evaluation)
        return asdict(evaluation)

    @app.get("/api/positions/{position_id}/candidates")
    def list_candidates(position_id: int, organization_id: int = Depends(current_organization)):
        find_position(organization_id, position_id)
        return storage.get_candidates(organization_id, position_id)

    return app


def position_to_json(position: Position) -> dict:
    return {
        "id": position.id,
        "title": position.title,
        "required_skills": position.required_skills,
        "criteria": [
            {"description": criterion.description(), "weight": criterion.weight}
            for criterion in position.criteria
        ],
        "skills": asked_skills(position),
    }


def asked_skills(position: Position) -> list[str]:
    skills = list(position.required_skills)
    for criterion in position.criteria:
        if isinstance(criterion, SkillCriterion) and criterion.skill not in skills:
            skills.append(criterion.skill)
    return skills
