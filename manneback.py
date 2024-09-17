from os import makedirs
import pandas as pd
import torch
from datasets     import load_dataset
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

# General info
token   = 'THIS_IS_SECRET'
device  = 'cuda' if torch.cuda.is_available() else 'cpu'
models  = {
    'llama3.1-8b' : 'meta-llama/Meta-Llama-3.1-8B-Instruct',
    #'mistral-nemo': 'mistralai/Mistral-Nemo-Instruct-2407',
    #'mistral-7b'  : 'mistralai/Mistral-7B-Instruct-v0.3',
}
print(f'model will run on {device}')

# prepare data
dataset = load_dataset("arch-be/brabant-xvii", name="doc_by_doc")
train   = dataset['train'].to_pandas()
valid   = dataset['valid'].to_pandas()
test    = dataset['test'].to_pandas()
dataset = pd.concat([train, test, valid]).set_index(['project', 'file_id'])
# start with the longest texts (fail fast)
dataset.sort_values(by='text', key=lambda x: x.str.len(), ascending=False, inplace=True)

with open('prompt.txt', encoding='utf8') as f:
    prompt = f.read()

# run the inference pipeline
for model, hf_key in models.items():
    makedirs(f'generated_texts/{model}/', exist_ok=True)
    #
    pipe = pipeline(
        'text-generation',
        model=hf_key,
        model_kwargs={'torch_dtype': torch.bfloat16},
        device=device,
        token=token,
        )

    interaction = lambda x: pipe(x, max_new_tokens=3000)
    #
    #interaction = lambda x: x
    for id, text in dataset['text'].items():
        project,file_id = id
        print(f'generated_texts/{model}/{project}_{file_id}')
        with open(f'generated_texts/{model}/{project}_{file_id}', 'w', encoding='utf8') as f:
            input_text = [
                {'role': 'system', 'content': prompt},
                {'role': 'user',   'content': text},
            ]
            print(interaction(input_text), file=f)
    #
    del interaction
    del pipe
