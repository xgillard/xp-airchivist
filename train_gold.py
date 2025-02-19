import json
import torch
import numpy  as np
import pandas as pd
from datasets import Dataset, DatasetDict
from transformers import (AutoModelForTokenClassification, 
                            AutoTokenizer, 
                            TrainingArguments, 
                            Trainer,
                            DataCollatorForTokenClassification,
                            EvalPrediction)
from seqeval.metrics import precision_score, recall_score, f1_score

# config de base
hftoken    = "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"
num_epochs = 80
batch_size = 64

# 1e chose: on charge le modele et son tokenizer
device    = "cuda" if torch.cuda.is_available() else "cpu"
checkpt   = "xaviergillard/xlm-roberta-large-vieille-france"
tokenizer = AutoTokenizer.from_pretrained(checkpt)
model     = AutoModelForTokenClassification.from_pretrained(checkpt, device_map="auto")
id2label  = model.config.id2label
label2id  = model.config.label2id 

# 2e chose: on charge le dataset et on prépare 3 sets de données (train, valid & test)
ds         = Dataset.from_parquet("./gold_standard.parquet")
splitted   = Dataset.train_test_split(ds.shuffle(), .2)
valid_test = Dataset.train_test_split(splitted["test"], .5)
ds = DatasetDict({
    "train": splitted['train'],
    "test" : valid_test["train"],
    "eval" : valid_test["test"],
})

# On crée des fonctions utilitaires qui vont nous permettre de mesurer 
# la performance du modele qu'on entraine.
def align_pred_labels(labels: np.ndarray, logits: np.ndarray) -> tuple[list[list[str]],list[list[str]]]:
    """
    Aligne les prédictions et les labels afin qu'on puisse calculer 
    les metriques d'évaluation avec sequeval
    """
    preds    = logits.argmax(axis=-1)
    l_result = []
    p_result = []
    for i, sample in enumerate(labels):
        l_curr = []
        p_curr = []
        l_result.append(l_curr)
        p_result.append(p_curr)
        
        #
        for j, token_label in enumerate(sample):
            if token_label != -100:
                l_curr.append(model.config.id2label[token_label])
                p_curr.append(model.config.id2label[preds[i,j]])
    return (l_result, p_result)


def compute_metrics(eval_pred: EvalPrediction) -> dict[str,float]: 
    labels, values = align_pred_labels(eval_pred.label_ids, eval_pred.predictions)
    return {
        'precision': precision_score(labels, values, average="micro"),
        'recall'   : recall_score(labels, values,    average="micro"),
        'f1'       : f1_score(labels, values,        average="micro"),
    }
    
# Préparation de l'entrainement à proprement parler
training_args = TrainingArguments(
    output_dir='./arch-be/xlm-roberta-vieille-france-v2',
    eval_strategy="epoch",
    num_train_epochs=num_epochs,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    save_strategy='epoch',
    push_to_hub=True, 
    push_to_hub_model_id='xlm-roberta-vieille-france-v2',
    push_to_hub_token=hftoken,
    save_total_limit=2,
)
trainer = Trainer(
    model           = model,
    args            = training_args,
    data_collator   = DataCollatorForTokenClassification(tokenizer),
    train_dataset   = ds['train'],
    eval_dataset    = ds["test"],
    compute_metrics = compute_metrics,
)   

# entrainement pour du vrai
trainer.train()
# Sauvegarder les métriques
metrics = trainer.evaluate(ds['eval'], metric_key_prefix = "eval_")
with open("./arch-be/xlm-roberta-vieille-france-v2/metrics.json", "w") as f:
    json.dump(metrics, f)
trainer.push_to_hub(commit_message="Upload model with metrics")

