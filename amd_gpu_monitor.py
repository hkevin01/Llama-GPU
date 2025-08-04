#!/usr/bin/env python3
"""
AMD GPU Performance Monitor for Llama-GPU
Monitors GPU usage, memory, and performance metrics
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime


def check_rocm_available():
    """Check if ROCm tools are available"""
    try:
        result = subprocess.run(['rocm-smi', '--help'],
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def get_gpu_info():
    """Get GPU information using rocm-smi"""
    if not check_rocm_available():
        return {"error": "rocm-smi not available"}

    try:
        # Get GPU information
        result = subprocess.run(['rocm-smi', '--showproductname'],
                              capture_output=True, text=True, timeout=5)
        gpu_names = []
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'Card' in line and ':' in line:
                    gpu_names.append(line.split(':')[1].strip())

        # Get memory info
        result = subprocess.run(['rocm-smi', '--showmeminfo', 'vram'],
                              capture_output=True, text=True, timeout=5)
        memory_info = {}
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'GPU' in line and 'Memory' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        gpu_id = parts[0]
                        used = parts[2] if len(parts) > 2 else "0"
                        total = parts[3] if len(parts) > 3 else "0"
                        memory_info[gpu_id] = {"used": used, "total": total}

        # Get temperature
        result = subprocess.run(['rocm-smi', '--showtemp'],
                              capture_output=True, text=True, timeout=5)
        temp_info = {}
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'GPU' in line and '°C' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        gpu_id = parts[0]
                        temp = parts[2].replace('°C', '')
                        temp_info[gpu_id] = temp

        return {
            "gpu_names": gpu_names,
            "memory": memory_info,
            "temperature": temp_info,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {"error": f"Failed to get GPU info: {e}"}

def get_pytorch_info():
    """Get PyTorch GPU information"""
    try:
        result = subprocess.run([
            sys.executable, '-c',
            """
import torch
import json

info = {
    'torch_version': torch.__version__,
    'hip_version': getattr(torch.version, 'hip', None),
    'cuda_available': torch.cuda.is_available(),
    'device_count': 0,
    'devices': []
}

if torch.cuda.is_available():
    info['device_count'] = torch.cuda.device_count()
    for i in range(torch.cuda.device_count()):
        device_info = {
            'id': i,
            'name': torch.cuda.get_device_name(i),
            'memory_allocated': torch.cuda.memory_allocated(i),
            'memory_cached': torch.cuda.memory_reserved(i),
            'memory_total': torch.cuda.get_device_properties(i).total_memory
        }
        info['devices'].append(device_info)

print(json.dumps(info, indent=2))
"""
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": f"PyTorch check failed: {result.stderr}"}

    except Exception as e:
        return {"error": f"Failed to get PyTorch info: {e}"}

def run_performance_test():
    """Run a simple GPU performance test"""
    try:
        print("🧪 Running GPU performance test...")
        result = subprocess.run([
            sys.executable, '-c',
            """
import torch
import time

if not torch.cuda.is_available():
    print("GPU not available for testing")
    exit(1)

device = torch.cuda.current_device()
print(f"Testing on device: {torch.cuda.get_device_name(device)}")

# Warm up
for _ in range(3):
    x = torch.randn(1000, 1000, device='cuda')
    y = torch.randn(1000, 1000, device='cuda')
    _ = torch.mm(x, y)

# Time matrix multiplication
sizes = [500, 1000, 2000]
for size in sizes:
    torch.cuda.synchronize()
    start_time = time.time()

    x = torch.randn(size, size, device='cuda')
    y = torch.randn(size, size, device='cuda')
    z = torch.mm(x, y)

    torch.cuda.synchronize()
    end_time = time.time()

    elapsed = end_time - start_time
    ops = 2 * size**3  # Approximate operations for matrix multiply
    gflops = (ops / elapsed) / 1e9

    print(f"Matrix size {size}x{size}: {elapsed:.3f}s ({gflops:.1f} GFLOPS)")

print("Performance test completed!")
"""
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ Performance test results:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"❌ Performance test failed: {result.stderr}")

    except Exception as e:
        print(f"⚠️ Performance test error: {e}")

def monitor_mode():
    """Continuous monitoring mode"""
    print("🔄 Starting continuous GPU monitoring...")
    print("Press Ctrl+C to stop")

    try:
        while True:
            os.system('clear')  # Clear screen
            print("🖥️  AMD GPU Monitor - Llama-GPU")
            print("=" * 50)
            print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
            print()

            # ROCm info
            gpu_info = get_gpu_info()
            if "error" not in gpu_info:
                print("🔧 ROCm GPU Status:")
                for i, gpu_name in enumerate(gpu_info.get("gpu_names", [])):
                    print(f"   GPU {i}: {gpu_name}")

                for gpu_id, mem in gpu_info.get("memory", {}).items():
                    temp = gpu_info.get("temperature", {}).get(gpu_id, "N/A")
                    print(f"   {gpu_id} Memory: {mem['used']}/{mem['total']} MB, Temp: {temp}°C")
            else:
                print(f"⚠️ ROCm status: {gpu_info['error']}")

            print()

            # PyTorch info
            pytorch_info = get_pytorch_info()
            if "error" not in pytorch_info:
                print("🐍 PyTorch GPU Status:")
                print(f"   Version: {pytorch_info['torch_version']}")
                if pytorch_info.get('hip_version'):
                    print(f"   ROCm/HIP: {pytorch_info['hip_version']}")
                print(f"   GPU Available: {pytorch_info['cuda_available']}")
                print(f"   Device Count: {pytorch_info['device_count']}")

                for device in pytorch_info.get('devices', []):
                    allocated_mb = device['memory_allocated'] / (1024**2)
                    cached_mb = device['memory_cached'] / (1024**2)
                    total_mb = device['memory_total'] / (1024**2)
                    print(f"   Device {device['id']}: {device['name']}")
                    print(f"      Memory: {allocated_mb:.1f}MB allocated, {cached_mb:.1f}MB cached, {total_mb:.1f}MB total")
            else:
                print(f"⚠️ PyTorch status: {pytorch_info['error']}")

            print()
            print("Press Ctrl+C to stop monitoring...")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")

def main():
    """Main function"""
    print("🚀 AMD GPU Performance Monitor for Llama-GPU")
    print("=" * 50)

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            run_performance_test()
            return
        elif sys.argv[1] == "monitor":
            monitor_mode()
            return
        elif sys.argv[1] == "info":
            pass  # Default behavior below

    # Show current status
    print("\n🔍 Current GPU Status:")
    print("-" * 30)

    # ROCm status
    gpu_info = get_gpu_info()
    if "error" not in gpu_info:
        print("✅ ROCm GPU Information:")
        for i, gpu_name in enumerate(gpu_info.get("gpu_names", [])):
            print(f"   GPU {i}: {gpu_name}")

        for gpu_id, mem in gpu_info.get("memory", {}).items():
            temp = gpu_info.get("temperature", {}).get(gpu_id, "N/A")
            print(f"   {gpu_id} Memory: {mem['used']}/{mem['total']} MB")
            print(f"   {gpu_id} Temperature: {temp}°C")
    else:
        print(f"⚠️ ROCm: {gpu_info['error']}")

    print()

    # PyTorch status
    pytorch_info = get_pytorch_info()
    if "error" not in pytorch_info:
        print("✅ PyTorch GPU Information:")
        print(f"   PyTorch Version: {pytorch_info['torch_version']}")
        if pytorch_info.get('hip_version'):
            print(f"   ROCm/HIP Version: {pytorch_info['hip_version']}")
        print(f"   GPU Available: {pytorch_info['cuda_available']}")
        print(f"   Device Count: {pytorch_info['device_count']}")

        for device in pytorch_info.get('devices', []):
            allocated_mb = device['memory_allocated'] / (1024**2)
            total_mb = device['memory_total'] / (1024**2)
            print(f"   Device {device['id']}: {device['name']}")
            print(f"   Memory Usage: {allocated_mb:.1f}MB / {total_mb:.1f}MB")
    else:
        print(f"⚠️ PyTorch: {pytorch_info['error']}")

    print("\n💡 Usage:")
    print("   python3 amd_gpu_monitor.py info    - Show current status")
    print("   python3 amd_gpu_monitor.py test    - Run performance test")
    print("   python3 amd_gpu_monitor.py monitor - Continuous monitoring")

if __name__ == "__main__":
    main()
