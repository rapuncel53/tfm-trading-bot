#!/bin/bash
set -e
export VIRTUAL_ENV="$HOME/tfm_env"
export PATH="$HOME/tfm_env/bin:$HOME/.local/bin:$PATH"

echo "Installing remaining packages with uv in $VIRTUAL_ENV..."
uv pip install "transformers>=4.48.0" "peft>=0.10.0" "bitsandbytes>=0.45.0" pandas pyarrow scipy tqdm openpyxl accelerate

echo "Verifying installation..."
python -c "import transformers, peft, bitsandbytes, pandas, pyarrow, scipy; print('All libraries imported successfully!')"
