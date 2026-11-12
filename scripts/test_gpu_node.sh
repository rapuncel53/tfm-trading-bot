#!/bin/bash
source $HOME/tfm_env/bin/activate
echo "--- HOST ---"
hostname
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader
echo "--- TORCH ---"
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('Device count:', torch.cuda.device_count()); print('Device name:', torch.cuda.get_device_name(0))"
echo "--- HF ACCESS & TOKENIZER ---"
python -c "from transformers import AutoTokenizer; tok = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B', trust_remote_code=True); print('Tokenizer loaded successfully!')" 2>&1 || python -c "from transformers import AutoTokenizer; tok = AutoTokenizer.from_pretrained('Qwen/Qwen3.5-9B', trust_remote_code=True); print('Qwen3.5 Tokenizer loaded successfully!')" 2>&1 || echo "Tokenizer test note"
