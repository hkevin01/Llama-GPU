# PyTorch ROCm Installation Guide

## Requirements

- AMD GPU with ROCm support
- ROCm 6.3 or later installed
- Linux operating system (Ubuntu 22.04 LTS recommended)
- Python 3.8 or later

## PyTorch Version

This project requires PyTorch with ROCm 6.3 support. The specific version needed is:

```bash
torch==2.7.1+rocm6.3
```

## Installation Steps

1. **Ensure ROCm is installed**

   ```bash
   # Check ROCm version
   rocm-smi --version
   ```

2. **Create and activate virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install PyTorch with ROCm support**

   ```bash
   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.3
   ```

4. **Verify Installation**

   ```python
   import torch
   print(f"PyTorch version: {torch.__version__}")
   print(f"ROCm version: {torch.version.hip}")
   print(f"GPU available: {torch.cuda.is_available()}")
   ```

## Troubleshooting

If you encounter any issues:

1. Make sure your AMD GPU is supported by ROCm 6.3
2. Verify that ROCm is properly installed and configured
3. Check that your system PATH includes ROCm binaries
4. Ensure you have the latest GPU drivers installed

For more detailed AMD GPU setup instructions, refer to `AMD_GPU_ACCELERATION_GUIDE.md` in the project root.

## Notes

- The installation may take some time as it downloads approximately 4.5GB of data
- Make sure you have sufficient disk space available
- A stable internet connection is recommended for the download
- The virtual environment should be activated before installing PyTorch

## Additional Resources

- [Official PyTorch ROCm Documentation](https://pytorch.org/get-started/locally/)
- [ROCm Documentation](https://rocmdocs.amd.com/en/latest/)
- [AMD ROCm GitHub](https://github.com/RadeonOpenCompute/ROCm)
