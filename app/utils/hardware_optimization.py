"""
Hardware optimization module for GAIA D&D Campaign Assistant.
Detects system hardware and optimizes configuration automatically.
"""

import os
import platform
import logging
import subprocess
from typing import Dict, Any

# Get the logger
logger = logging.getLogger("GAIA")

def detect_hardware() -> Dict[str, Any]:
    """
    Detect hardware specifications of the system.
    
    Returns:
        Dictionary containing hardware details
    """
    hardware_info = {
        "system": platform.system(),
        "processor": "Unknown",
        "cores": os.cpu_count() or 4,
        "memory_gb": 8,  # Default assumption
        "gpu": "None"
    }
    
    try:
        # Get processor information
        if platform.system() == "Windows":
            try:
                output = subprocess.check_output("wmic cpu get name", shell=True).decode()
                processor_name = output.strip().split('\n')[-1].strip()
                hardware_info["processor"] = processor_name
                
                # Get memory information
                mem_output = subprocess.check_output("wmic ComputerSystem get TotalPhysicalMemory", shell=True).decode()
                total_memory = int(mem_output.strip().split('\n')[-1].strip())
                hardware_info["memory_gb"] = round(total_memory / (1024**3))
                
                # Try to detect GPU
                try:
                    gpu_output = subprocess.check_output("wmic path win32_VideoController get name", shell=True).decode()
                    gpu_lines = gpu_output.strip().split('\n')[1:]
                    if gpu_lines:
                        hardware_info["gpu"] = gpu_lines[0].strip()
                except:
                    pass
                
            except Exception as e:
                logger.warning(f"Error detecting Windows hardware: {e}")
                
        elif platform.system() == "Linux":
            try:
                # Get processor info
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.strip().startswith('model name'):
                            hardware_info["processor"] = line.split(':')[1].strip()
                            break
                
                # Get memory info
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.strip().startswith('MemTotal'):
                            mem_kb = int(line.split(':')[1].strip().split()[0])
                            hardware_info["memory_gb"] = round(mem_kb / (1024**2))
                            break
                            
                # Try to detect GPU
                try:
                    gpu_output = subprocess.check_output("lspci | grep -i 'vga\\|3d\\|2d'", shell=True).decode()
                    if gpu_output:
                        hardware_info["gpu"] = gpu_output.strip().split(':')[-1].strip()
                except:
                    pass
                    
            except Exception as e:
                logger.warning(f"Error detecting Linux hardware: {e}")
                
        elif platform.system() == "Darwin":  # macOS
            try:
                # Get processor info
                output = subprocess.check_output("sysctl -n machdep.cpu.brand_string", shell=True).decode()
                hardware_info["processor"] = output.strip()
                
                # Get memory info
                mem_output = subprocess.check_output("sysctl -n hw.memsize", shell=True).decode()
                mem_bytes = int(mem_output.strip())
                hardware_info["memory_gb"] = round(mem_bytes / (1024**3))
                
                # Try to detect GPU
                try:
                    gpu_output = subprocess.check_output("system_profiler SPDisplaysDataType | grep 'Chipset Model'", shell=True).decode()
                    if gpu_output:
                        hardware_info["gpu"] = gpu_output.split(':')[1].strip()
                except:
                    pass
                    
            except Exception as e:
                logger.warning(f"Error detecting macOS hardware: {e}")
                
    except Exception as e:
        logger.warning(f"Hardware detection failed: {e}")
    
    return hardware_info

def optimize_config(config, hardware_info: Dict[str, Any]) -> None:
    """
    Optimize configuration based on detected hardware.
    
    Args:
        config: Configuration object to optimize
        hardware_info: Dictionary with hardware details
    """
    # Log detected hardware
    logger.info(f"Detected system: {hardware_info['system']}")
    logger.info(f"Processor: {hardware_info['processor']}")
    logger.info(f"CPU Cores: {hardware_info['cores']}")
    logger.info(f"Memory: {hardware_info['memory_gb']} GB")
    logger.info(f"GPU: {hardware_info['gpu']}")
    
    # Optimize for AMD processors
    if "AMD" in hardware_info["processor"]:
        logger.info("AMD processor detected, applying optimizations")
        
        # Ryzen-specific optimizations
        if "Ryzen" in hardware_info["processor"]:
            # AMD Ryzen typically benefits from thread count matching physical cores
            if hardware_info["cores"] >= 8:
                config.n_threads = 8
            elif hardware_info["cores"] >= 6:
                config.n_threads = 6
            else:
                config.n_threads = max(4, hardware_info["cores"])
                
            # AMD Ryzen benefits from larger batch sizes
            config.n_batch = 768
            
            logger.info(f"Set n_threads to {config.n_threads}")
            logger.info(f"Set n_batch to {config.n_batch}")
    
    # Optimize for Intel processors
    elif "Intel" in hardware_info["processor"]:
        logger.info("Intel processor detected, applying optimizations")
        
        # Intel typically gets better performance with slightly fewer threads
        config.n_threads = max(1, min(hardware_info["cores"] - 2, 8))
        
        # Default batch size works well for Intel
        config.n_batch = 512
        
        logger.info(f"Set n_threads to {config.n_threads}")
    
    # Memory-based optimizations
    if hardware_info["memory_gb"] >= 16:
        # With 16+ GB, we can use a larger context window
        config.n_ctx = 8192
        logger.info(f"Set n_ctx to {config.n_ctx}")
    elif hardware_info["memory_gb"] >= 8:
        # With 8-16 GB, use a medium context window
        config.n_ctx = 4096
        logger.info(f"Set n_ctx to {config.n_ctx}")
    else:
        # With less than 8 GB, use a smaller context window
        config.n_ctx = 2048
        logger.info(f"Set n_ctx to {config.n_ctx}")
    
    # GPU detection
    if "NVIDIA" in hardware_info["gpu"]:
        logger.info("NVIDIA GPU detected")
        # Set GPU layers if NVIDIA GPU detected
        config.n_gpu_layers = 32
        logger.info(f"Set n_gpu_layers to {config.n_gpu_layers}")
    elif "AMD" in hardware_info["gpu"] and "Radeon" in hardware_info["gpu"]:
        logger.info("AMD Radeon GPU detected (not currently utilized)")
        # Keep GPU layers at 0 as llama.cpp doesn't well support AMD GPUs yet
        config.n_gpu_layers = 0
    else:
        # No GPU or unsupported GPU
        config.n_gpu_layers = 0