#!/bin/bash
# Make all AMD GPU scripts executable

echo "🔧 Setting up AMD GPU acceleration scripts..."

cd /home/kevin/Projects/Llama-GPU

# Make scripts executable
chmod +x complete_amd_setup.sh
chmod +x advanced_amd_setup.sh
chmod +x check_amd_status.py
chmod +x amd_gpu_monitor.py
chmod +x amd_gpu_check.py

echo "✅ All scripts are now executable"

echo ""
echo "📋 Available AMD GPU Commands:"
echo "   ./complete_amd_setup.sh           - Quick ROCm PyTorch setup"
echo "   ./advanced_amd_setup.sh           - Advanced setup with options"
echo "   python3 check_amd_status.py       - Check current status"
echo "   python3 amd_gpu_monitor.py info   - GPU information"
echo "   python3 amd_gpu_monitor.py test   - Performance test"
echo "   python3 amd_gpu_monitor.py monitor - Live monitoring"

echo ""
echo "🎯 Quick Start:"
echo "   1. Run: ./complete_amd_setup.sh"
echo "   2. Test: python3 check_amd_status.py"
echo "   3. Monitor: python3 amd_gpu_monitor.py monitor"

echo ""
echo "📖 Full documentation: AMD_GPU_ACCELERATION_GUIDE.md"
