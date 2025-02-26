"""Les outils nécessaires pour executer une passe de NER sur un texte relativement long."""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

import pandas as pd
import torch
from scipy.special import softmax

if TYPE_CHECKING:
    from numpy import ndarray
    from torch import Tensor
    from transformers import (
        AutoModelForTokenClassification,
        BatchEncoding,
        PreTrainedTokenizer,
    )
    from transformers.modeling_outputs import TokenClassifierOutput


class NerRecord(NamedTuple):
    """Un tag ner appliqué à un bout de texte."""

    span_start: int
    span_end: int
    length: int
    entity: int
    label: str


class Ner:
    """Un pipeline de Named Entity Recognition qui utilise mon modele 'vieille france' basé sur XLM-Roberta.

    # Hypotèse
    Comme il s'agit d'un modèle multilingue et qui a été spécifiquement préentrainé
    pour être multilingue, on peut espérer qu'un cross-lingual transfer puisse avoir
    lieu (et donc, qu'on soit capable de retrouver les entités voulues dans un texte
    qui ne soit pas en vieux français ==> par ex vieux néérlandais).

    # Hypothèse 2
    Un truc a tester, c'est qu'il est possible qu'il faille "domain-adapter" le modele
    de base en fine-tunant son objectif MLM sur un corpus qui comprenne à la fois du
    vieux néérlandais ET du vieux francais.

    # Note et Intérêt Technique
    Même s'il est parfaitement inenvisageable d'utiliser d'entrainer ce modèle en
    utilisant uniquement le CPU d'un laptop, on peut parfaitement faire l'inférence
    dans ces conditions là. Ca passe très bien.
    """

    _tokenizer: PreTrainedTokenizer
    _model: AutoModelForTokenClassification

    def __init__(
        self,
        tokenizer: PreTrainedTokenizer,
        model: AutoModelForTokenClassification,
    ) -> None:
        """Crée le pipeline NER.

        ## Params
        - tokenizer : le tokenizer du modèle
        - model     : le modèle qui a été fine tuné pour la NER
        """
        self._tokenizer = tokenizer
        self._model = model

    def __call__(
        self,
        txt: str,
        stride: int = 0,
        simplify: bool = True,  # noqa: FBT001, FBT002
        aggressive: bool = True,  # noqa: FBT001, FBT002
    ) -> pd.DataFrame:
        """Effectue un tour complet dans le pipeline de NER.

        Renvoie un dictionnaire comprenant les différentes entités qui ont été
        retrouvées dans le texte. Si le flag 'simplify' est True, alors les
        records redondants sont supprimés. Si le flag 'aggressive' est True
        en plus du flag 'simplify', alors plus de records redondants seront supprimés.
        """
        encoded: pd.DataFrame = self._encode(txt, stride=stride)
        decoded: pd.DataFrame = self._decode(txt, encoded)
        postpro: pd.DataFrame = self._postprocess(txt, decoded)
        if simplify:
            return self.simplify(postpro, aggressive)
        return postpro

    def _encode(self, text: str, stride: int = 0) -> pd.DataFrame:
        """Encode les tags du texte dans un dataframe.

        Renvoie un dataframe avec 4 colonnes:
        - input_ids: les identifiants correspondant à chaque sous-mot du texte
        - tokens   : la représentation de chacun des sous-mots du texte en entrée
        - labels   : les tags qui ont été prédits pour chacun des sous-mots du texte en entrée
        - offsets  : le mapping 'début,fin' pour chaque token indiquant l'endroit du texte
                     ou se trouve l'objet labellisé.
        """
        max_length: int = self._model.config.max_length
        tokenized: BatchEncoding = self._tokenizer(
            text,
            return_tensors="pt",
            return_offsets_mapping=True,
            return_overflowing_tokens=True,
            truncation=True,
            max_length=max_length,
            padding=True,
            pad_to_multiple_of=max_length,
            add_special_tokens=True,
            stride=stride,
        )
        ### actually process the input
        input_ids: Tensor = tokenized["input_ids"].to(self._model.device)
        attn_mask: Tensor = tokenized["attention_mask"].to(self._model.device)
        offsets: ndarray = tokenized["offset_mapping"].detach().numpy()
        offsets: list[tuple[int, int]] = [(a, b) for seq in offsets for a, b in seq]
        output: TokenClassifierOutput = self._model.forward(
            input_ids=input_ids,
            attention_mask=attn_mask,
        )
        logits: ndarray = output.logits.cpu().detach().to(torch.float32).numpy()
        proba: ndarray = softmax(logits, axis=-1)
        predicted: ndarray = proba.argmax(axis=-1)
        ### postprocess the outputs
        input_ids: ndarray = input_ids.cpu().detach().numpy()
        attn_mask: Tensor = attn_mask.cpu().detach()
        input_ids: ndarray = input_ids.reshape(-1)
        tokens: list[str] = self._tokenizer.convert_ids_to_tokens(input_ids)
        predicted: ndarray = predicted.reshape(-1)
        labels: list[str] = [self._model.config.id2label[x] for x in predicted]
        result: pd.DataFrame = pd.DataFrame(
            {"input_ids": input_ids, "tokens": tokens, "labels": labels, "offsets": offsets},
        )
        return result

    def _decode(self, original: str, encoded: pd.DataFrame) -> pd.DataFrame:  # noqa: C901
        """Renvoie un dataframe reprenant les différentes entités qui ont été retrouvées dans le texte encodé."""
        tokens, tags, offsets = encoded.tokens, encoded.labels, encoded.offsets
        _entities: list[str] = []
        _labels: list[str] = []
        _start: list[int] = []
        _end: list[int] = []

        prev = None
        bgn, end = 0, 0

        def save_current_entity() -> None:
            """Utilise le contexte (non local) de la fonction pour sauver l'entité courante.

            L'entité est retrouvée directement dans le texte du document qu'on est en train de traiter.
            """
            nonlocal _entities
            nonlocal _labels
            nonlocal _start
            nonlocal _end
            _entities.append(original[bgn : end + 1])
            _labels.append(prev)
            _start.append(bgn)
            _end.append(end)

        for tok, tag, offset in zip(tokens, tags, offsets):
            if prev and not tok.startswith("▁"):  # it is not the beginning of a word -> assign previous tag
                end = max(offset[1], end)
            else:
                match tag:
                    case "O":
                        if bgn != end:
                            save_current_entity()
                        prev = None
                        bgn, end = end, end  # noqa: PLW0127
                    case _ if tag.startswith("B-"):
                        if bgn != end:
                            save_current_entity()
                        tt = tag[2:]
                        prev = tt
                        bgn, end = offset
                    case _ if tag.startswith("I-"):
                        tt = tag[2:]
                        if prev == tt and offset[1] > end:
                            end = offset[1]
        if bgn != end:
            save_current_entity()
        return pd.DataFrame({"entity": _entities, "label": _labels, "span_start": _start, "span_end": _end})

    def _postprocess(self, text: str, decoded: pd.DataFrame) -> pd.DataFrame:
        """Effectue une passe de postprocessing sur les entités décodées.

        Le postprocessing sert à joindre les différents bouts d'entité qui pourraient
        avoir été éparpillés durant le processus de tagging. Plusieurs entités ne sont
        jointes que ssi elles ont toutes le meme tag et elles couvrent des portions du
        texte qui se superposent
        """
        df: pd.DataFrame = decoded.sort_values(["span_start", "span_end"])
        #### MERGE TO CREATE LONGEST POSSIBLE SEQUENCE
        records = set()
        for i in range(len(df)):
            row = df.iloc[i]
            b, e = row.span_start, row.span_end
            relevant = range(b, e + 1)
            matching = df[df.span_start.isin(relevant) | df.span_end.isin(relevant)]
            if matching.label.nunique() == 1:  # noqa: PD101
                l_merged = row.label
                b_merged = matching.span_start.min()
                e_merged = matching.span_end.max()
                t_merged = text[b_merged : e_merged + 1]
                records.add(NerRecord(b_merged, e_merged, e_merged - b_merged, t_merged, l_merged))
            else:
                start = row.span_start
                end = row.span_end
                entity = row.entity
                label = row.label
                records.add(NerRecord(start, end, end - start, entity, label))
        df: pd.DataFrame = pd.DataFrame(records)
        ##### DROP DANGLING SUBSTRINGS
        remove = []
        for i in range(len(df)):
            row = df.iloc[i]
            b, e = row.span_start, row.span_end
            length = row.length
            matching = df[
                (
                    (df.length > length)
                    & (((df.span_start <= b) & (df.span_end >= b)) | ((df.span_start <= e) & (df.span_end >= e)))
                )
            ]
            if not matching.empty:
                remove.append(i)
        df: pd.DataFrame = df.drop(remove)
        #df: pd.DataFrame = df.drop(columns=["length"])
        return df.set_index(["span_start", "span_end"])

    def simplify(self, df: pd.DataFrame, aggressive: bool = True) -> pd.DataFrame:  # noqa: FBT001, FBT002
        """Supprime certains records qui sont jugés redondants.

        Si le flag 'aggressive' est True, alors on va non seulement supprimer
        les records qui sont des duplicats exacts, mais aussi ceux qui sont
        des sous chaines strictes d'autres entrées labellisées avec le meme tag.
        """
        df2 = df.reset_index()
        df2["entity"] = df2["entity"].str.replace("\n", " ").str.strip()
        df2 = df2.drop(columns=["span_start", "span_end"])
        df2 = df2.drop_duplicates()

        if aggressive:
            drop = []
            for row in df2.iterrows():
                i, (entity, label) = row
                length = len(entity)
                matching = df2[
                    (df2.entity.str.contains(entity) & (df2.entity.str.len() > length) & (df2.label == label))
                ]
                if not matching.empty:
                    drop.append(i)
            df2 = df2.drop(index=drop)
        return df2
