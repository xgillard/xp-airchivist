from __future__ import annotations

import json
import sqlite3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:3000",  # development react
    "http://www.arch.be",
    "http://arch.be",
    "*",
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
    ranking: int


@app.get("/nb_docs")
def nb_docs() -> int:
    """Renvoie le nombre de documents dans le corpus."""
    return 419


@app.get("/by_id/{identifier}")
def by_id(identifier: int) -> LabeledData:
    """Renvoie un item labellisé par tous les modeles."""
    text, llama = by_model_id("llama", identifier)
    _, mistral7b = by_model_id("mistral7b", identifier)
    _, mistralnemo = by_model_id("mistralnemo", identifier)
    _, vieille_france = vf_by_model_id("vieille_france", identifier)
    return LabeledData(
        identifier=identifier,
        text=text,
        docdata={
            "llama": llama,
            "mistral7b": mistral7b,
            "mistralnemo": mistralnemo,
            "vieille_france": vieille_france,
        },
    )


@app.post("/ranking")
def set_ranking(request: RankingRequest) -> None:
    """Enregistre le ranking de la labelisation d'un modele."""
    with sqlite3.connect(f"./databases/{request.model}.db") as con:
        cursor = con.cursor()
        cursor.execute("UPDATE dataset SET ranking = ? WHERE id = ?", (request.ranking, request.identifier))


def by_model_id(model: str, identifier: int) -> (str | None, ModelData | None):
    """Renvoie un item labellisé par un modele."""
    with sqlite3.connect(f"./databases/{model}.db") as con:
        cursor = con.cursor()
        cursor.execute("SELECT text, labeling, ranking FROM dataset WHERE id = ?", (identifier,))
        text, labeling, ranking = cursor.fetchone()
        labeling = json.loads(labeling)
        docdata = labeling["documentdata"]

        persons = sorted([f"{p['firstname']} {p['lastname']}".lower() for p in docdata["persons"]])
        locations = sorted([loc["name"].lower() for loc in docdata["locations"]])
        dates = sorted([docdata["act_date"].lower(), docdata["fact_date"].lower()])
        return text, ModelData(model=model, ranking=ranking, persons=persons, locations=locations, dates=dates)


def vf_by_model_id(model: str, identifier: int) -> (str | None, ModelData | None):
    """Renvoie une donnée labellisée par le modele vieille france."""
    with sqlite3.connect(f"./databases/{model}.db") as con:
        cursor = con.cursor()
        cursor.execute("SELECT text, labeling, ranking FROM dataset WHERE id = ?", (identifier,))
        text, labeling, ranking = cursor.fetchone()
        labeling = json.loads(labeling)
        persons = sorted([p.lower() for p in labeling["persons"]])
        locations = sorted([loc.lower() for loc in labeling["locations"]])
        dates = sorted([d.lower() for d in labeling["dates"]])
        return text, ModelData(model=model, ranking=ranking, persons=persons, locations=locations, dates=dates)
