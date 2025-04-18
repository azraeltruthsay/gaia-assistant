#!/usr/bin/env python3
"""
Code Repository Uploader for GAIA.

This script imports code repositories into GAIA's knowledge base. It handles:
1. Copying code files to the external code directory
2. Filtering out binary files, large files, and other non-relevant content
3. Creating an initial directory structure summary
"""

import os
import sys
import re
import shutil
import argparse
import logging
from datetime import datetime
from typing import List, Set, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/code_uploader.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CODE_UPLOADER")

# Files and directories to exclude
EXCLUDE_PATTERNS = [
    # Binary files
    r'\.exe$', r'\.dll$', r'\.so$', r'\.dylib$', r'\.a$', r'\.lib$',
    r'\.obj$', r'\.o$', r'\.pyc$', r'\.pyo$', r'\.pyd$',
    r'\.png$', r'\.jpg$', r'\.jpeg$', r'\.gif$', r'\.bmp$', r'\.ico$',
    r'\.mp3$', r'\.mp4$', r'\.wav$', r'\.avi$', r'\.mov$', r'\.mkv$',
    r'\.zip$', r'\.tar$', r'\.gz$', r'\.7z$', r'\.rar$',
    r'\.bin$', r'\.dat$', r'\.db$', r'\.sqlite$', r'\.sqlite3$',
    r'\.pdf$', r'\.doc$', r'\.docx$', r'\.xls$', r'\.xlsx$', r'\.ppt$', r'\.pptx$',
    
    # Version control directories
    r'/\.git/', r'/\.svn/', r'/\.hg/',
    
    # Environment and cache directories
    r'/venv/', r'/\.venv/', r'/env/', r'/\.env/',
    r'/__pycache__/', r'/\.pytest_cache/', r'/\.mypy_cache/',
    r'/node_modules/', r'/bower_components/',
    r'/\.idea/', r'/\.vscode/',
    
    # Large generated files
    r'/dist/', r'/build/', r'/coverage/', r'/\.coverage/',
    r'\.min\.js$', r'\.min\.css$',
    r'\.gguf$', r'\.ggml$', r'\.bin$', r'\.pt$', r'\.pth$',
    
    # Log files
    r'\.log$',
    
    # Other specific exclusions
    r'\.DS_Store$', r'Thumbs\.db$',
    r'\.env$', r'\.env\.local$', r'\.env\.development$', r'\.env\.production$',
]

# Compile all patterns for faster matching
EXCLUDE_REGEX = [re.compile(pattern) for pattern in EXCLUDE_PATTERNS]

# Maximum file size to process (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

def is_excluded(path: str) -> bool:
    """
    Check if a path should be excluded.
    
    Args:
        path: File or directory path to check
        
    Returns:
        True if path should be excluded, False otherwise
    """
    """
    Check if a path should be excluded.
    
    Args:
        path: File or directory path to check
        
    Returns:
        True if path should be excluded, False otherwise
    """
    # Check against all exclude patterns
    return any(regex.search(path) for regex in EXCLUDE_REGEX)

def is_text_file(filepath: str) -> bool:
    """
    Check if a file is a text file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        True if file is a text file, False otherwise
    """
    try:
        # Check file size
        if os.path.getsize(filepath) > MAX_FILE_SIZE:
            return False
            
        # Try to read the first few bytes as text
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except UnicodeDecodeError:
        # Try another common encoding
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                f.read(1024)
            return True
        except:
            return False
    except:
        return False

def copy_repository(source_path: str, target_path: str) -> Dict[str, Any]:
    """
    Copy a repository to the target path, filtering out excluded files.
    
    Args:
        source_path: Source repository path
        target_path: Target path for the copy
        
    Returns:
        Dictionary with statistics about the copy operation
    """
    if not os.path.exists(source_path):
        raise ValueError(f"Source path does not exist: {source_path}")
        
    # Create target directory if it doesn't exist
    os.makedirs(target_path, exist_ok=True)
    
    stats = {
        'total_files': 0,
        'copied_files': 0,
        'excluded_files': 0,
        'binary_files': 0,
        'large_files': 0,
        'languages': {},
        'extensions': {}
    }
    
    # Walk through the source directory
    for root, dirs, files in os.walk(source_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not is_excluded(os.path.join(root, d))]
        
        for file in files:
            src_file_path = os.path.join(root, file)
            stats['total_files'] += 1
            
            # Skip excluded files
            if is_excluded(src_file_path):
                stats['excluded_files'] += 1
                continue
                
            # Skip large files
            if os.path.getsize(src_file_path) > MAX_FILE_SIZE:
                stats['large_files'] += 1
                continue
                
            # Check if it's a text file
            if not is_text_file(src_file_path):
                stats['binary_files'] += 1
                continue
                
            # Create relative path
            rel_path = os.path.relpath(src_file_path, source_path)
            dst_file_path = os.path.join(target_path, rel_path)
            
            # Create target directory if it doesn't exist
            os.makedirs(os.path.dirname(dst_file_path), exist_ok=True)
            
            # Copy the file
            shutil.copy2(src_file_path, dst_file_path)
            stats['copied_files'] += 1
            
            # Track file extensions
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            if ext:
                stats['extensions'][ext] = stats['extensions'].get(ext, 0) + 1
                
            # Determine language based on extension
            language = determine_language(ext)
            if language:
                stats['languages'][language] = stats['languages'].get(language, 0) + 1
                
    return stats

def determine_language(extension: str) -> Optional[str]:
    """
    Determine programming language based on file extension.
    
    Args:
        extension: File extension
        
    Returns:
        Language name or None if unknown
    """
    extension = extension.lower().lstrip('.')
    
    language_map = {
        'py': 'Python',
        'js': 'JavaScript',
        'jsx': 'JavaScript (React)',
        'ts': 'TypeScript',
        'tsx': 'TypeScript (React)',
        'java': 'Java',
        'c': 'C',
        'cpp': 'C++',
        'h': 'C/C++ Header',
        'hpp': 'C++ Header',
        'cs': 'C#',
        'go': 'Go',
        'rb': 'Ruby',
        'php': 'PHP',
        'html': 'HTML',
        'htm': 'HTML',
        'css': 'CSS',
        'scss': 'SCSS',
        'less': 'LESS',
        'json': 'JSON',
        'xml': 'XML',
        'yaml': 'YAML',
        'yml': 'YAML',
        'md': 'Markdown',
        'rs': 'Rust',
        'swift': 'Swift',
        'kt': 'Kotlin',
        'pl': 'Perl',
        'sh': 'Shell',
        'bash': 'Bash',
        'bat': 'Batch',
        'ps1': 'PowerShell',
        'sql': 'SQL',
        'r': 'R',
        'dart': 'Dart',
        'lua': 'Lua',
        'scala': 'Scala',
        'groovy': 'Groovy',
        'dockerfile': 'Dockerfile',
        'graphql': 'GraphQL',
        'vue': 'Vue',
    }
    
    return language_map.get(extension)

def create_summary_file(repo_path: str, stats: Dict[str, Any], output_path: str) -> None:
    """
    Create a summary markdown file for the repository.
    
    Args:
        repo_path: Path to the repository
        stats: Statistics about the repository
        output_path: Path to write the summary file
    """
    repo_name = os.path.basename(repo_path.rstrip('/\\'))
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Repository Summary: {repo_name}\n\n")
        f.write(f"Generated on: {timestamp}\n\n")
        
        f.write("## Statistics\n\n")
        f.write(f"- **Total Files**: {stats['total_files']}\n")
        f.write(f"- **Copied Files**: {stats['copied_files']}\n")
        f.write(f"- **Excluded Files**: {stats['excluded_files']}\n")
        f.write(f"- **Binary Files**: {stats['binary_files']}\n")
        f.write(f"- **Large Files**: {stats['large_files']}\n\n")
        
        if stats['languages']:
            f.write("## Languages\n\n")
            for language, count in sorted(stats['languages'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{language}**: {count} files\n")
            f.write("\n")
            
        if stats['extensions']:
            f.write("## File Extensions\n\n")
            for ext, count in sorted(stats['extensions'].items(), key=lambda x: x[1], reverse=True)[:20]:  # Top 20
                f.write(f"- **{ext}**: {count} files\n")
            f.write("\n")
            
        # Generate directory structure
        f.write("## Directory Structure\n\n")
        f.write("```\n")
        directory_structure = generate_directory_structure(repo_path)
        f.write(directory_structure)
        f.write("```\n")

def generate_directory_structure(path: str, prefix: str = "", max_depth: int = 3) -> str:
    """
    Generate a tree-like directory structure string.
    
    Args:
        path: Path to generate structure for
        prefix: Prefix for the current line
        max_depth: Maximum depth to recurse
        
    Returns:
        String representation of the directory structure
    """
    if max_depth <= 0:
        return f"{prefix}...\n"
        
    output = ""
    
    # Get the base name of the path
    base_name = os.path.basename(path.rstrip('/\\'))
    if not base_name:  # In case path ends with / or \
        base_name = os.path.basename(os.path.dirname(path))
    
    output += f"{prefix}{base_name}/\n"
    
    try:
        entries = list(sorted(os.scandir(path), key=lambda e: e.name))
        
        # Filter out excluded entries
        entries = [e for e in entries if not is_excluded(e.path)]
        
        # Process directories first, then files
        dirs = [e for e in entries if e.is_dir()]
        files = [e for e in entries if e.is_file()]
        
        # Limit the number of items shown
        if len(dirs) > 10:
            dirs = dirs[:10]
            output += f"{prefix}│   [... {len(dirs) - 10} more directories ...]\n"
            
        if len(files) > 20:
            files = files[:20]
            output += f"{prefix}│   [... {len(files) - 20} more files ...]\n"
        
        # Process directories
        for i, entry in enumerate(dirs):
            is_last = (i == len(dirs) - 1) and not files
            new_prefix = prefix + ("└── " if is_last else "├── ")
            child_prefix = prefix + ("    " if is_last else "│   ")
            output += generate_directory_structure(entry.path, new_prefix, max_depth - 1)
        
        # Process files
        for i, entry in enumerate(files):
            is_last = (i == len(files) - 1)
            output += f"{prefix}{'└── ' if is_last else '├── '}{entry.name}\n"
    except PermissionError:
        output += f"{prefix}│   [Permission denied]\n"
    except Exception as e:
        output += f"{prefix}│   [Error: {str(e)}]\n"
    
    return output

def main():
    parser = argparse.ArgumentParser(description="Import code repositories into GAIA's knowledge base.")
    parser.add_argument("source", help="Source repository path")
    parser.add_argument("--target", default="./external-code", help="Target path for repository")
    parser.add_argument("--name", help="Repository name (defaults to source directory name)")
    
    args = parser.parse_args()
    
    source_path = os.path.abspath(args.source)
    
    if not args.name:
        repo_name = os.path.basename(source_path.rstrip('/\\'))
    else:
        repo_name = args.name
    
    target_path = os.path.join(args.target, repo_name)
    
    try:
        print(f"Importing repository: {repo_name}")
        print(f"Source: {source_path}")
        print(f"Target: {target_path}")
        
        # Copy the repository
        print("\nCopying files...")
        stats = copy_repository(source_path, target_path)
        
        print("\nRepository Import Statistics:")
        print(f"Total files: {stats['total_files']}")
        print(f"Copied files: {stats['copied_files']}")
        print(f"Excluded files: {stats['excluded_files']}")
        print(f"Binary files: {stats['binary_files']}")
        print(f"Large files: {stats['large_files']}")
        
        # Create summary file
        summary_path = os.path.join(target_path, "REPOSITORY_SUMMARY.md")
        create_summary_file(source_path, stats, summary_path)
        print(f"\nSummary file created: {summary_path}")
        
        print(f"\nRepository import complete. The code is now ready to be processed by GAIA.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        logger.error(f"Error importing repository: {e}", exc_info=True)
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())