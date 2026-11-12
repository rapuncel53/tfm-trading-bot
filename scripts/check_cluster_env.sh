#!/bin/bash
echo "=== HOST & GPU CHECK ==="
hostname
nvidia-smi 2>&1 || echo "nvidia-smi not available on login node"

echo "=== VENV STATUS ==="
if [ -d "$HOME/tfm_env" ]; then
    echo "tfm_env directory exists"
    $HOME/tfm_env/bin/python --version
    $HOME/tfm_env/bin/python -m pip --version 2>&1 || echo "pip not installed"
    $HOME/tfm_env/bin/python -c "import torch; print('Torch:', torch.__version__, 'CUDA available:', torch.cuda.is_available())" 2>&1 || echo "Torch not importable"
    $HOME/tfm_env/bin/python -c "import transformers, peft, bitsandbytes; print('LLM stack OK')" 2>&1 || echo "LLM stack incomplete"
else
    echo "tfm_env does not exist"
fi

echo "=== SLURM NODES ==="
sinfo -o "%20P %5a %10l %16F %N"
squeue
