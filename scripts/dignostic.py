import torch
import subprocess

def check_gpu():
    print("--- 🔍 PyTorch VRAM Diagnostic ---")
    if torch.cuda.is_available():
        print(f"✅ GPU Detected: {torch.cuda.get_device_name(0)}")
        # PyTorch tracks active memory usage in bytes, so we convert to GB
        allocated = torch.cuda.memory_allocated(0) / 1024**3
        reserved = torch.cuda.memory_reserved(0) / 1024**3
        print(f"Memory Allocated: {allocated:.2f} GB")
        print(f"Memory Reserved by Caching Allocator: {reserved:.2f} GB")
    else:
        print("❌ PyTorch cannot see the GPU. It is defaulting to the CPU.")

    print("\n--- 📊 System nvidia-smi Snapshot ---")
    try:
        # Runs the standard NVIDIA management utility to check hardware-level stats
        subprocess.run(["nvidia-smi"])
    except FileNotFoundError:
        print("nvidia-smi command not found. Ensure NVIDIA drivers are correctly configured in Arch.")

if __name__ == "__main__":
    check_gpu()
