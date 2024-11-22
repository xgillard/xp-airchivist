from __future__ import annotations

import sqlite3
from functools import partial
from typing import TYPE_CHECKING

import pandas as pd
import torch
from pydantic import BaseModel
from tqdm import tqdm
from transformers import AutoModelForTokenClassification, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer

from ner import Ner

if TYPE_CHECKING:
    from typing import Self


class DocData(BaseModel):
    """Les résultats d'une tache de labellisation ou on veut trouver les personnes, les lieux et les dates."""

    persons: list[str]
    locations: list[str]
    dates: list[str]

    @staticmethod
    def from_dataframe(df: pd.DataFrame) -> Self:
        """Convertit un dataframe en une instance de DocData."""
        converted: dict[str, list[str]] = to_dict(df)
        return DocData(
            persons=converted.get("PERS", []),
            locations=converted.get("LOC", []),
            dates=converted.get("DATE", []),
        )


def to_dict(df: pd.DataFrame) -> dict[str, list[str]]:
    """Convertit un dataframe de tags ner en un dictionnaire groupé par tag."""
    result = {}
    for _, row in df.iterrows():
        lst = result.get(row.label, [])
        if not lst:
            result[row.label] = lst
        lst.append(row.entity)
    return result


def pipeline(ner: Ner, text: str, /, stride: int = 20, indent: int = 0) -> str:
    """Execute un pipeline ner complet pour un document et renvoie le docdata en json."""
    return DocData.from_dataframe(ner(text, stride=stride)).model_dump_json(indent=indent)


def main() -> None:
    """Execute the main entry point of the program."""
    checkpoint = "xaviergillard/xlm-roberta-large-vieille-france"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tqdm.pandas()
    with torch.no_grad():
        tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained(checkpoint)
        model: PreTrainedModel = AutoModelForTokenClassification.from_pretrained(
            checkpoint,
            torch_dtype=torch.bfloat16,
        ).to(device)
        model.eval()
        ner: Ner = Ner(tokenizer, model)

        pipe: partial = partial(pipeline, ner, stride=20)

        with sqlite3.connect("../language.db") as con:
            df: pd.DataFrame = pd.read_sql("select id, text, language from dataset", con).set_index(["id"])

            df["labeling"] = df["text"].progress_map(pipe)
            df.to_csv("vieille_france.csv", index=True, index_label="id")


if __name__ == "__main__":
    main()
