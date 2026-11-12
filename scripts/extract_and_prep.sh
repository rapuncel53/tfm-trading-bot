#!/bin/bash
set -e
echo "Creating ~/tfm and extracting project_transfer.tar.gz..."
mkdir -p $HOME/tfm
tar -xzf $HOME/project_transfer.tar.gz -C $HOME/tfm
rm -f $HOME/project_transfer.tar.gz

echo "Directory structure of ~/tfm:"
ls -lh $HOME/tfm
ls -lh $HOME/tfm/data/splits/train
ls -lh $HOME/tfm/checkpoints/llm_return_regressor
echo "SUCCESS: Extraction completed."
