import numpy  as np
import pandas as pd

from transformers import AutoTokenizer
from datasets     import load_dataset


dataset = load_dataset('arch-be/brabant-xvii', name='doc_by_doc')

train = dataset['train'].to_pandas()
train['split'] = 'train'

valid = dataset['valid'].to_pandas()
valid['split'] = 'valid'

test = dataset['test'].to_pandas()
test['split'] = 'test'

df = pd.concat([train, test, valid])
df['project'] = df['project'].astype('category')
df['split']   = df['split'].astype('category')
df.set_index(["split", "project", "file_id"])

df.to_parquet("brabant-xvii.parquet", index=True, compression='gzip')