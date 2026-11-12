#!/bin/bash
source $HOME/tfm_env/bin/activate
python -c "
from transformers import AutoConfig
try:
    c = AutoConfig.from_pretrained('Qwen/Qwen3.5-9B', trust_remote_code=True)
    print('Found Qwen/Qwen3.5-9B, hidden size:', getattr(c, 'hidden_size', None))
except Exception as e:
    print('Qwen/Qwen3.5-9B not found:', e)

try:
    c2 = AutoConfig.from_pretrained('Qwen/Qwen2.5-7B', trust_remote_code=True)
    print('Found Qwen/Qwen2.5-7B, hidden size:', getattr(c2, 'hidden_size', None))
except Exception as e:
    print('Qwen/Qwen2.5-7B not found:', e)
"
