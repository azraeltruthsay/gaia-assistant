#!/usr/bin/env python3
"""
Campaign Tools - Utility script for managing D&D campaign content
"""

import os
import sys
import argparse
import shutil
import glob
from datetime import datetime

# Default paths (can be overridden with command line args)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CAMPAIGN_DATA = os.path.join(PROJECT_ROOT, "campaign-data")
CORE_DOCS = os.path.join(CAMPAIGN_DATA, "core-documentation")
GEN_DOCS = os.path.join(CAMPAIGN_DATA, "generated_documentation")
RAW_DATA = os.path.join(CAMPAIGN_DATA, "raw-data")

def ensure_directories():
    """Ensure all required directories exist"""
    for path in [CAMPAIGN_DATA, CORE_DOCS, GEN_DOCS, RAW_DATA]:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created directory: {path}")

def backup_campaign():
    """Create a timestamped backup of all campaign data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"campaign_backup_{timestamp}"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Copy all campaign data to backup directory
    try:
        shutil.copytree(CAMPAIGN_DATA, os.path.join(backup_dir, "campaign-data"))
        print(f"Campaign data backed up to {backup_dir}")
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False

def create_template(template_type, name):
    """Create a new template file based on specified type"""
    ensure_directories()
    
    templates = {
        "location": """# {name}
**Version: 1.0**

## SECTION I: OVERVIEW
- **Name**: {name}
- **Location**: 
- **Status**: 
- **Significance**: 

## SECTION II: DESCRIPTION
### Physical Features
- 

### Notable Areas
- 

## SECTION III: INHABITANTS
- 

## SECTION IV: HISTORY
- 

## SECTION V: POINTS OF INTEREST
- 

## SECTION VI: CONNECTIONS
- 
""",
        "npc": """# {name}
**Version: 1.0**

## SECTION I: BASIC INFORMATION
- **Name**: {name}
- **Race/Species**: 
- **Gender**: 
- **Occupation/Role**: 
- **Location**: 

## SECTION II: APPEARANCE
- 

## SECTION III: PERSONALITY
- 

## SECTION IV: ABILITIES & RESOURCES
- 

## SECTION V: MOTIVATIONS & GOALS
- 

## SECTION VI: CONNECTIONS
- 

## SECTION VII: NOTES & SECRETS
- 
""",
        "item": """# {name}
**Version: 1.0**

## SECTION I: BASIC INFORMATION
- **Name**: {name}
- **Type**: 
- **Rarity**: 
- **Location**: 
- **Creator**: 

## SECTION II: APPEARANCE
- 

## SECTION III: PROPERTIES
- 

## SECTION IV: HISTORY
- 

## SECTION V: NOTES
- 
"""
    }
    
    if template_type not in templates:
        print(f"Unknown template type: {template_type}")
        print(f"Available types: {', '.join(templates.keys())}")
        return False
    
    # Create filename with correct formatting
    safe_name = name.replace(' ', '_').lower()
    filename = os.path.join(CORE_DOCS, f"{safe_name}.md")
    
    # Don't overwrite existing files
    if os.path.exists(filename):
        print(f"Error: File {filename} already exists!")
        return False
    
    # Write template to file
    with open(filename, 'w') as f:
        f.write(templates[template_type].format(name=name))
    
    print(f"Created {template_type} template: {filename}")
    return True

def list_files(directory=None, pattern=None):
    """List files in the specified directory with optional pattern matching"""
    if directory is None:
        directory = CORE_DOCS
    
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return False
    
    if pattern:
        files = glob.glob(os.path.join(directory, pattern))
    else:
        files = [os.path.join(directory, f) for f in os.listdir(directory) 
                 if os.path.isfile(os.path.join(directory, f))]
    
    if not files:
        print(f"No files found in {directory}" + (f" matching {pattern}" if pattern else ""))
        return False
    
    print(f"Files in {directory}" + (f" matching {pattern}" if pattern else ""))
    for f in sorted(files):
        print(f"  - {os.path.basename(f)}")
    
    return True

def extract_headers(filepath):
    """Extract and display markdown headers from a file"""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    headers = []
    for line in content.split('\n'):
        if line.strip().startswith('#'):
            headers.append(line.strip())
    
    if not headers:
        print(f"No headers found in {filepath}")
        return False
    
    print(f"Headers in {os.path.basename(filepath)}:")
    for header in headers:
        # Count leading # characters to determine level
        level = len(header) - len(header.lstrip('#'))
        indent = "  " * (level - 1)
        print(f"{indent}{header.strip('# ')}")
    
    return True

def main():
    """Main function for parsing arguments and running commands"""
    parser = argparse.ArgumentParser(description="Campaign Tools - Utility for managing D&D campaign content")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create a backup of campaign data')
    
    # Create template command
    template_parser = subparsers.add_parser('create', help='Create a new template file')
    template_parser.add_argument('type', choices=['location', 'npc', 'item'], help='Template type')
    template_parser.add_argument('name', help='Name for the new entity')
    
    # List files command
    list_parser = subparsers.add_parser('list', help='List files in campaign directories')
    list_parser.add_argument('--dir', choices=['core', 'gen', 'raw'], default='core', 
                           help='Directory to list (default: core)')
    list_parser.add_argument('--pattern', help='File pattern to match (e.g., "*.md")')
    
    # Show outline command
    outline_parser = subparsers.add_parser('outline', help='Show outline of a markdown file')
    outline_parser.add_argument('file', help='File to show outline for')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Ensure directories exist
    ensure_directories()
    
    # Execute appropriate command
    if args.command == 'backup':
        backup_campaign()
    elif args.command == 'create':
        create_template(args.type, args.name)
    elif args.command == 'list':
        # Map directory choice to actual path
        dir_map = {
            'core': CORE_DOCS,
            'gen': GEN_DOCS,
            'raw': RAW_DATA
        }
        list_files(dir_map[args.dir], args.pattern)
    elif args.command == 'outline':
        extract_headers(args.file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
