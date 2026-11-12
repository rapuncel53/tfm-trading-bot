#!/bin/bash
source $HOME/tfm_env/bin/activate
python -c "
import torch
ckpt = torch.load('$HOME/tfm/checkpoints/llm_return_regressor/best_model.pt', map_location='cpu', weights_only=False)
sd = ckpt['model_state_dict'] if isinstance(ckpt, dict) and 'model_state_dict' in ckpt else ckpt
print('Total keys in best_model.pt:', len(sd))
head_weight = [v for k, v in sd.items() if 'forecasting_head.linear.weight' in k]
if head_weight:
    print('Forecasting head weight shape:', head_weight[0].shape)
lora_weight = [v for k, v in sd.items() if 'lora_A' in k]
if lora_weight:
    print('Sample LoRA weight shape:', lora_weight[0].shape)
"
