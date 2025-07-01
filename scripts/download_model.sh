#!/bin/bash
# Script to download LLaMA model weights from HuggingFace or Meta
# Usage: ./download_model.sh <model_name> <output_dir>

MODEL_NAME=$1
OUTPUT_DIR=$2

if [ -z "$MODEL_NAME" ] || [ -z "$OUTPUT_DIR" ]; then
  echo "Usage: $0 <model_name> <output_dir>"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Example using HuggingFace CLI (requires login)
huggingface-cli download $MODEL_NAME --local-dir "$OUTPUT_DIR"

echo "Model $MODEL_NAME downloaded to $OUTPUT_DIR"
