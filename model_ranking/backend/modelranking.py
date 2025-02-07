from __future__ import annotations

import json
import sqlite3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:5173",  # development react
    "http://modelranking-rest.arch.be",
    "http://modelranking.arch.be",
    "http://www.arch.be",
    "http://arch.be",
    "https://modelranking-rest.arch.be",
    "https://modelranking.arch.be",
    "https://www.arch.be",
    "https://arch.be",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LabeledData(BaseModel):
    """Données labellisées par tous les modeles."""

    identifier: int
    text: str
    docdata: dict[str, ModelData]


class ModelData(BaseModel):
    """Donnée labellisée par un modele."""

    model: str
    ranking: int | None
    persons: list[str]
    locations: list[str]
    dates: list[str]


class RankingRequest(BaseModel):
    """Requete pour stocker un ranking."""

    identifier: str
    model: str
    usrname: str
    ranking: int


@app.get("/nb_docs")
def nb_docs() -> int:
    """Renvoie le nombre de documents dans le corpus."""
    return 419


@app.get("/by_id/{identifier}/{usrname}")
def by_id(identifier: int, usrname: str) -> LabeledData:
    """Renvoie un item labellisé par tous les modeles."""
    text, llama = by_model_id("llama", identifier, usrname)
    _, mistral7b = by_model_id("mistral7b", identifier, usrname)
    _, mistralnemo = by_model_id("mistralnemo", identifier, usrname)
    _, gpt4omini = by_model_id("gpt4o-mini", identifier, usrname)
    _, vieille_france = by_model_id("vieille_france", identifier, usrname)
    return LabeledData(
        identifier=identifier,
        text=text,
        docdata={
            "llama": llama,
            "mistral7b": mistral7b,
            "mistralnemo": mistralnemo,
            "gpt4o-mini": gpt4omini,
            "vieille_france": vieille_france,
        },
    )


@app.post("/ranking")
def set_ranking(request: RankingRequest) -> None:
    """Enregistre le ranking de la labelisation d'un modele."""
    with sqlite3.connect("./databases/unified.db") as con:
        cursor = con.cursor()
        cursor.execute(
            """INSERT INTO ranking(id, model, usrname, ranking)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(id, model, usrname) DO UPDATE SET
                   ranking = ?;""",
            (request.identifier, request.model, request.usrname, request.ranking, request.ranking))


@app.get("/todo/{lang}/{usrname}")
def todo(lang: str, usrname: str) -> int | None:
    """Renvoie l'id d'un document dans la langue voulue qui n'est pas encore traité par l'utilisateur."""
    with sqlite3.connect("./databases/unified.db") as con:
        cursor = con.cursor()
        cursor.execute("""
            SELECT d.id
            FROM documents d
            WHERE d.lang = ?
            AND EXISTS (
                SELECT l.model
                FROM   labeling l
                WHERE  l.id = d.id
                AND NOT EXISTS (
                    SELECT r.ranking
                    FROM  ranking r
                    WHERE r.id      = l.id
                    AND   r.model   = l.model
                    AND   r.usrname = ?
                )
            )
            ORDER BY RANDOM();
        """, (lang, usrname))
        return cursor.fetchone()[0]

def by_model_id(model: str, identifier: int, usrname: str) -> tuple[str | None, ModelData | None]:
    """Renvoie un item labellisé par un modele."""
    with sqlite3.connect("./databases/unified.db") as con:
        cursor = con.cursor()
        cursor.execute("""
            SELECT d.text, l.labeling
            FROM documents d
            JOIN labeling l ON d.id = l.id
            WHERE
                d.id      = ?  AND
                l.model   = ? """,
            (identifier, model))
        text, labeling = cursor.fetchone()
        # retrieve the user ranking (if it exists)
        cursor.execute("""
            SELECT ranking 
            FROM ranking r
            WHERE r.id = ?
            AND   r.model = ?
            AND r.usrname = ?""",
            (identifier, model, usrname))
        ranking = cursor.fetchone()
        ranking = ranking[0] if ranking is not None else 0
        labeling = json.loads(labeling)
        if model == "vieille_france":
            persons = sorted([p.lower() for p in labeling["persons"]])
            locations = sorted([loc.lower() for loc in labeling["locations"]])
            dates = sorted([d.lower() for d in labeling["dates"]])
            return text, ModelData(model=model, ranking=ranking, persons=persons, locations=locations, dates=dates)
        else:  # noqa: RET505
            docdata   = labeling.get("documentdata")
            persons   = []
            locations = []
            dates     = []
            if docdata and docdata.get("persons"):
                persons   = sorted([f"{p['firstname']} {p['lastname']}".lower() for p in docdata["persons"]])
            if docdata and docdata.get("locations"):
                locations = sorted([loc["name"].lower() for loc in docdata["locations"]])
            if docdata:
                dates = sorted([docdata["act_date"].lower(), docdata["fact_date"].lower()])
            return text, ModelData(model=model, ranking=ranking, persons=persons, locations=locations, dates=dates)
