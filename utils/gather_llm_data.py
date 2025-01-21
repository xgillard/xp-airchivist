import pandas as pd

# models data sheet
huggingface = pd.DataFrame.from_dict([
# mistral
{'id': 'mistral-7b',    'key': 'mistralai/Mistral-7B-Instruct-v0.3'   },
{'id': 'mistral-8x7b',  'key': 'mistralai/Mixtral-8x7B-Instruct-v0.1' },
{'id': 'mistral-nemo',  'key': 'mistralai/Mistral-Nemo-Instruct-2407' },
{'id': 'mistral-8x22b', 'key': 'mistralai/Mixtral-8x22B-v0.1'         },
{'id': 'mistral-large', 'key': 'mistralai/Mistral-Large-Instruct-2407'},
# gpt
{'id': 'gpt2',          'key': 'openai-community/gpt2'                }, 
# llama
{'id': 'llama3.1-8b',   'key':  'meta-llama/Meta-Llama-3.1-8B-Instruct'},
{'id': 'llama3.1-70b',  'key':  'meta-llama/Meta-Llama-3.1-70B-Instruct'},
{'id': 'llama3.1-405b', 'key':  'meta-llama/Meta-Llama-3.1-405B-Instruct'},
# dedicated
{'id': 'gysbertv2',     'key':  'xaviergillard/brabant-xvii-shallow'},
{'id': 'xlm-roberta',   'key':  'xaviergillard/xlm-roberta-large-vieille-france'},
{'id': 'from-scratch',  'key':  'xaviergillard/brabant-xvii-from-scratch'},
]).set_index(["id"])

context = pd.DataFrame.from_dict([
# mistral
{'id': 'mistral-7b',    'context':  32e3},
{'id': 'mistral-8x7b',  'context':  32e3},
{'id': 'mistral-nemo',  'context': 128e3},    
{'id': 'mistral-8x22b', 'context':  64e3},    
{'id': 'mistral-large', 'context': 128e3},
# gpt
{'id': 'gpt4o',         'context': 128e3},
{'id': 'gpt4o-mini',    'context': 128e3},
{'id': 'gpt4-turbo',    'context': 128e3},
{'id': 'gpt3.5-turbo',  'context':  16e3},
{'id': 'gpt2',          'context': 1024},
# llama
{'id': 'llama3.1-8b',   'context':  128e3},
{'id': 'llama3.1-70b',  'context':  128e3},
{'id': 'llama3.1-405b', 'context':  128e3},
# dedicated
{'id': 'gysbertv2',     'context':  512},
{'id': 'xlm-roberta',   'context':  512},
{'id': 'from-scratch',  'context':  512},
]).set_index(["id"])

params = pd.DataFrame.from_dict([
# mistral
{'id': 'mistral-7b',    'params':  7.25e9},
{'id': 'mistral-8x7b',  'params':  46.7e9},
{'id': 'mistral-nemo',  'params': 12.2e9},    
{'id': 'mistral-8x22b', 'params':  141e9},    
{'id': 'mistral-large', 'params': 123e9},
# gpt
{'id': 'gpt3.5-turbo',  'params': 175e9},
{'id': 'gpt2',          'params': 137e6},
# llama
{'id': 'llama3.1-8b',   'params':  8.03e9},
{'id': 'llama3.1-70b',  'params':  70.06e9},
{'id': 'llama3.1-405b', 'params':  405e9},
# dedicated
{'id': 'gysbertv2',     'params':  109e6},
{'id': 'xlm-roberta',   'params':  559e6},
{'id': 'from-scratch',  'params':  105e6},
]).set_index(["id"])

pricing = pd.DataFrame.from_dict([
# mistral
{'id': 'mistral-7b',    'in': 0.2,  'out': 0.2},
{'id': 'mistral-8x7b',  'in': 0.65, 'out': 0.65},
{'id': 'mistral-nemo',  'in': 0.27, 'out': 0.27},    
{'id': 'mistral-8x22b', 'in': 1.9,  'out': 5.6},    
{'id': 'mistral-large', 'in': 2.7,  'out': 8.2},
# gpt
{'id': 'gpt4o',         'in': 5,    'out': 15},
{'id': 'gpt4o-mini',    'in': 0.15, 'out': 0.6},
{'id': 'gpt4-turbo',    'in': 60,   'out': 120},
{'id': 'gpt3.5-turbo',  'in': 1.5,  'out': 2},
]).set_index(["id"])

mmlu = pd.DataFrame.from_dict([
# mistral
{'id': 'mistral-7b',    'mmlu': 62.5},
{'id': 'mistral-8x7b',  'mmlu': 70.6},
{'id': 'mistral-nemo',  'mmlu': 68},    
{'id': 'mistral-8x22b', 'mmlu': 77.75},    
{'id': 'mistral-large', 'mmlu': 76.9},
# gpt
{'id': 'gpt4o',         'mmlu': 88.7},
{'id': 'gpt4o-mini',    'mmlu': 82.0},
{'id': 'gpt4-turbo',    'mmlu': 86.4},
{'id': 'gpt3.5-turbo',  'mmlu': 70.0},
# llama
{'id': 'llama3.1-8b',   'mmlu': 73.0},
{'id': 'llama3.1-70b',  'mmlu': 86.0},
{'id': 'llama3.1-405b', 'mmlu': 88.6},
]).set_index(['id'])

llms = huggingface.join(context, how='outer').join(params, how='outer').join(pricing, how='outer').join(mmlu, how='outer')

huggingface.to_parquet('llm_data/huggingface.parquet', index=True, compression='gzip')
context.to_parquet('llm_data/context.parquet', index=True, compression='gzip')
params.to_parquet('llm_data/params.parquet', index=True, compression='gzip')
pricing.to_parquet('llm_data/pricing.parquet', index=True, compression='gzip')
mmlu.to_parquet('llm_data/mmlu.parquet', index=True, compression='gzip')
llms.to_parquet('llm_data/llm_data.parquet', index=True, compression='gzip')