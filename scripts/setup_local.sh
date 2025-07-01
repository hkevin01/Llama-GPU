#!/bin/bash
# Script to set up local environment for Llama-GPU

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
