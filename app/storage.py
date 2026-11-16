import json
import sqlite3

from app.domain.criteria import create_criterion
from app.domain.models import Candidate, Evaluation, Position

SCHEMA = """
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations (id),
    title TEXT NOT NULL,
    required_skills TEXT NOT NULL,
    criteria TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organizations (id),
    position_id INTEGER NOT NULL REFERENCES positions (id),
    name TEXT NOT NULL,
    skills TEXT NOT NULL,
    experience_years REAL,
    salary_expectation REAL,
    score REAL,
    recommendation TEXT NOT NULL,
    explanation TEXT NOT NULL,
    note TEXT NOT NULL
);
"""


class Storage:
    def __init__(self, path: str):
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(SCHEMA)

    def add_organization(self, name: str) -> int:
        with self.connection:
            cursor = self.connection.execute("INSERT INTO organizations (name) VALUES (?)", (name,))
        return cursor.lastrowid

    def get_organizations(self) -> list[dict]:
        rows = self.connection.execute("SELECT id, name FROM organizations ORDER BY id").fetchall()
        return [dict(row) for row in rows]

    def organization_exists(self, organization_id: int) -> bool:
        row = self.connection.execute(
            "SELECT id FROM organizations WHERE id = ?", (organization_id,)
        ).fetchone()
        return row is not None

    def add_position(
        self, organization_id: int, title: str, required_skills: list[str], criteria: list[dict]
    ) -> int:
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO positions (organization_id, title, required_skills, criteria) VALUES (?, ?, ?, ?)",
                (organization_id, title, to_json(required_skills), to_json(criteria)),
            )
        return cursor.lastrowid

    def get_positions(self, organization_id: int) -> list[Position]:
        rows = self.connection.execute(
            "SELECT * FROM positions WHERE organization_id = ? ORDER BY id", (organization_id,)
        ).fetchall()
        return [to_position(row) for row in rows]

    def get_position(self, organization_id: int, position_id: int) -> Position | None:
        row = self.connection.execute(
            "SELECT * FROM positions WHERE organization_id = ? AND id = ?",
            (organization_id, position_id),
        ).fetchone()
        if row is None:
            return None
        return to_position(row)

    def add_candidate(
        self, organization_id: int, position_id: int, candidate: Candidate, evaluation: Evaluation
    ) -> int:
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO candidates (organization_id, position_id, name, skills, experience_years,"
                " salary_expectation, score, recommendation, explanation, note)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    organization_id,
                    position_id,
                    candidate.name,
                    to_json(candidate.skills),
                    candidate.experience_years,
                    candidate.salary_expectation,
                    evaluation.score,
                    evaluation.recommendation,
                    to_json(evaluation.explanation),
                    evaluation.note,
                ),
            )
        return cursor.lastrowid

    def get_candidates(self, organization_id: int, position_id: int) -> list[dict]:
        rows = self.connection.execute(
            "SELECT name, score, recommendation, explanation, note FROM candidates"
            " WHERE organization_id = ? AND position_id = ? ORDER BY score DESC",
            (organization_id, position_id),
        ).fetchall()
        candidates = []
        for row in rows:
            candidate = dict(row)
            candidate["explanation"] = json.loads(row["explanation"])
            candidates.append(candidate)
        return candidates


def to_json(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def to_position(row: sqlite3.Row) -> Position:
    return Position(
        id=row["id"],
        title=row["title"],
        required_skills=json.loads(row["required_skills"]),
        criteria=[create_criterion(data) for data in json.loads(row["criteria"])],
    )
