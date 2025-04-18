#!/usr/bin/env python3
"""
GAIA Performance Benchmark

Tests different configurations to find optimal settings for your hardware.
"""

import os
import sys
import time
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/benchmark.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GAIA_BENCHMARK")

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import application components
from app.config import Config
from app.models.ai_manager import AIManager

# Standard test queries
TEST_QUERIES = [
    "Describe the relationship between Heimr and Brænēage.",
    "What is BlueShot and how is it used in Brænēage?",
    "Who is Anton Snark and what is his significance?",
    "Explain the concept of Primordis and Nondis in the cosmic structure."
]

def benchmark(threads, batch_size, ctx_size, num_runs=1, query_index=0):
    """
    Benchmark a specific configuration.
    
    Args:
        threads: Number of CPU threads
        batch_size: Batch size for processing
        ctx_size: Context window size
        num_runs: Number of test runs to average
        query_index: Index of the test query to use
        
    Returns:
        Dictionary with benchmark results or None if initialization failed
    """
    # Create custom config
    config = Config()
    config.n_threads = threads
    config.n_batch = batch_size
    config.n_ctx = ctx_size
    
    print(f"\nTesting configuration: threads={threads}, batch={batch_size}, ctx={ctx_size}")
    print("-" * 50)
    
    # Use a different query each time
    query = TEST_QUERIES[query_index % len(TEST_QUERIES)]
    print(f"Test query: {query[:50]}..." if len(query) > 50 else query)
    
    try:
        # Time for initialization
        init_start = time.time()
        
        # Initialize AI Manager
        ai_manager = AIManager(config)
        init_success = ai_manager.initialize()
        
        init_time = time.time() - init_start
        
        if not init_success:
            print("❌ Initialization failed")
            return None
        
        print(f"✅ Initialization time: {init_time:.2f} seconds")
        
        # Run the query multiple times and average results
        response_times = []
        memory_usage = []
        
        for run in range(num_runs):
            print(f"Run {run+1}/{num_runs}...")
            
            # Run standard test query
            query_start = time.time()
            response = ai_manager.query_campaign_world(query)
            query_time = time.time() - query_start
            
            response_times.append(query_time)
            print(f"  Query time: {query_time:.2f} seconds")
            
            # Try to get memory usage
            try:
                import psutil
                process = psutil.Process(os.getpid())
                mem = process.memory_info().rss / (1024 * 1024)  # MB
                memory_usage.append(mem)
                print(f"  Memory usage: {mem:.2f} MB")
            except ImportError:
                pass
        
        # Calculate average times
        avg_response_time = sum(response_times) / len(response_times)
        avg_memory = sum(memory_usage) / len(memory_usage) if memory_usage else 0
        
        return {
            "threads": threads,
            "batch_size": batch_size,
            "ctx_size": ctx_size,
            "init_time": init_time,
            "avg_response_time": avg_response_time,
            "avg_memory_mb": avg_memory,
            "success": True
        }
    
    except Exception as e:
        logger.error(f"Benchmark error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return None

def quick_benchmark():
    """Run a quick benchmark with a default set of configurations."""
    print("Running quick benchmark...")
    
    configs = [
        # Conservative settings
        (4, 512, 4096),
        # Balanced settings
        (6, 768, 4096),
        # Performance settings
        (8, 512, 8192),
        # Memory-intensive settings
        (8, 768, 8192)
    ]
    
    results = []
    for i, (threads, batch, ctx) in enumerate(configs):
        result = benchmark(threads, batch, ctx, num_runs=1, query_index=i)
        if result:
            results.append(result)
    
    return results

def ryzen7_4700u_benchmark():
    """Run a benchmark optimized for AMD Ryzen 7 4700U."""
    print("Running benchmark optimized for AMD Ryzen 7 4700U...")
    
    configs = [
        # Thread variations (8 cores on Ryzen 7 4700U)
        (6, 768, 4096),
        (7, 768, 4096),
        (8, 768, 4096),
        # Batch size variations
        (8, 512, 4096),
        (8, 768, 4096),
        (8, 1024, 4096),
        # Context size variations
        (8, 768, 4096),
        (8, 768, 8192)
    ]
    
    results = []
    for i, (threads, batch, ctx) in enumerate(configs):
        result = benchmark(threads, batch, ctx, num_runs=1, query_index=i % len(TEST_QUERIES))
        if result:
            results.append(result)
    
    return results

def save_results(results, benchmark_type):
    """Save benchmark results to a file."""
    if not results:
        print("No results to save.")
        return
    
    # Create results directory if it doesn't exist
    os.makedirs("benchmark_results", exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_results/{benchmark_type}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {filename}")

def print_results(results):
    """Print benchmark results in a formatted table."""
    if not results:
        print("No results to display.")
        return
    
    # Sort results by response time
    sorted_results = sorted(results, key=lambda x: x["avg_response_time"])
    
    # Print header
    print("\nResults (sorted by response time):")
    print("-" * 80)
    print(f"{'Threads':^10} | {'Batch':^10} | {'Context':^10} | {'Init (s)':^10} | {'Query (s)':^10} | {'Memory (MB)':^15}")
    print("-" * 80)
    
    # Print results
    for result in sorted_results:
        print(f"{result['threads']:^10} | {result['batch_size']:^10} | {result['ctx_size']:^10} | "
              f"{result['init_time']:.2f}s".center(10) + " | " +
              f"{result['avg_response_time']:.2f}s".center(10) + " | " +
              f"{result['avg_memory_mb']:.2f} MB".center(15))
    
    # Print best configuration
    best = sorted_results[0]
    print("\n" + "=" * 40)
    print("Best configuration:")
    print(f"Threads: {best['threads']}")
    print(f"Batch size: {best['batch_size']}")
    print(f"Context size: {best['ctx_size']}")
    print(f"Average query time: {best['avg_response_time']:.2f} seconds")
    print("=" * 40)
    
    # Return best config for easy copy-paste
    return best

def main():
    """Main benchmark function."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    print("=" * 60)
    print("GAIA Performance Benchmark".center(60))
    print("=" * 60)
    print("\nThis tool will help you find the optimal GAIA configuration for your hardware.")
    
    # Menu options
    print("\nSelect benchmark type:")
    print("1. Quick benchmark (recommended for first run)")
    print("2. Ryzen 7 4700U optimized benchmark")
    print("3. Custom benchmark")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == "1":
        results = quick_benchmark()
        best = print_results(results)
        save_results(results, "quick")
        
    elif choice == "2":
        results = ryzen7_4700u_benchmark()
        best = print_results(results)
        save_results(results, "ryzen7_4700u")
        
    elif choice == "3":
        print("\nCustom benchmark configuration:")
        
        try:
            threads = int(input("Number of threads (2-16): "))
            batch = int(input("Batch size (128-2048): "))
            ctx = int(input("Context size (2048, 4096, or 8192): "))
            runs = int(input("Number of test runs (1-5): "))
            
            result = benchmark(threads, batch, ctx, num_runs=runs)
            if result:
                results = [result]
                print_results(results)
                save_results(results, "custom")
        except ValueError:
            print("Invalid input. Please enter numeric values.")
            
    elif choice == "4":
        print("Exiting...")
        return
        
    else:
        print("Invalid choice.")
        return
    
    # Update docker-compose recommendation
    if 'best' in locals():
        print("\nFor docker-compose.yml:")
        print(f"""
  environment:
    N_THREADS: {best['threads']}
    N_BATCH: {best['batch_size']}
    N_CTX: {best['ctx_size']}
        """)

if __name__ == "__main__":
    main()