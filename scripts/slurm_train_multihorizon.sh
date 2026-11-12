#!/bin/bash
# ==============================================================================
# SLURM Submission Script: Entrenamiento Multi-Horizonte LLM (TFM)
# Cluster: slurmcm.epsem.upc.edu
# ==============================================================================

#SBATCH --job-name=tfm_multihorizon
#SBATCH --partition=merit
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=slurm_logs/%x_%j.out
#SBATCH --error=slurm_logs/%x_%j.err

echo "=========================================================="
echo "  Inicio de Trabajo SLURM: $(date)"
echo "  Nodo asignado: $(hostname)"
echo "  Job ID: $SLURM_JOB_ID"
echo "  CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"
echo "=========================================================="

cd $HOME/tfm
# 1. Crear directorios de logs si no existen
mkdir -p slurm_logs checkpoints/llm_return_regressor checkpoints/multimodal

# 2. Información de GPU
echo -e "\n[Hardware] Diagnóstico de GPU asignada:"
nvidia-smi

# 3. Activar entorno virtual
export VIRTUAL_ENV="$HOME/tfm_env"
export PATH="$HOME/tfm_env/bin:$PATH"

echo -e "\n[Python] Entorno activo:"
which python
python --version
python -c "import torch; print('PyTorch:', torch.__version__, '| CUDA available:', torch.cuda.is_available(), '| Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

# 4. Lanzar el entrenamiento Multi-Horizonte
echo -e "\n[Ejecución] Lanzando scripts/train_multihorizon_llm.py..."
python scripts/train_multihorizon_llm.py

EXIT_CODE=$?
echo "=========================================================="
echo "  Fin de Trabajo SLURM: $(date) (Exit code: $EXIT_CODE)"
echo "=========================================================="
exit $EXIT_CODE
