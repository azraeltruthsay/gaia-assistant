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

#  Adjusted paths for container compatibility
#  These should align with your docker-compose mounts
PROJECT_ROOT = "/app/projects"  #  Root of projects within the container
CAMPAIGN_DATA = os.path.join(PROJECT_ROOT, "dnd-campaign")
CORE_DOCS = os.path.join(CAMPAIGN_DATA, "core-documentation")
GEN_DOCS = os.path.join(CAMPAIGN_DATA, "generated_documentation")
RAW_DATA = os.path.join(CAMPAIGN_DATA, "raw-data")


def ensure_directories():
    """Ensure all required directories exist (within the container)"""
    for path in [CAMPAIGN_DATA, CORE_DOCS, GEN_DOCS, RAW_DATA]:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)  #  Use exist_ok to prevent errors if they exist
            print(f"Created directory: {path}")


def backup_campaign():
    """Create a timestamped backup of all campaign data (corrected)"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join("/app", f"campaign_backup_{timestamp}")  #  Ensure backup in /app

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir, exist_ok=True)

    try:
        #  Instead of copying the CAMPAIGN_DATA directory itself,
        #  copy its contents directly into the backup directory
        for item in os.listdir(CAMPAIGN_DATA):
            source_item = os.path.join(CAMPAIGN_DATA, item)
            dest_item = os.path.join(backup_dir, item)
            if os.path.isdir(source_item):
                shutil.copytree(source_item, dest_item)
            else:
                shutil.copy2(source_item, dest_item)  #  copy2 preserves metadata

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
""",
    }

    if template_type not in templates:
        print(f"Unknown template type: {template_type}")
        print(f"Available types: {', '.join(templates.keys())}")
        return False

    # Create filename with correct formatting
    safe_name = name.replace(" ", "_").lower()
    filename = os.path.join(CORE_DOCS, f"{safe_name}.md")

    # Don't overwrite existing files
    if os.path.exists(filename):
        print(f"Error: File {filename} already exists!")
        return False

    # Write template to file
    with open(filename, "w") as f:
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
        files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)]
    if not files:
        print(f"No files found in {directory}" + (f" matching {pattern}" if pattern else ""))
        return False
    print(f"Files in {directory}" + (f" matching {pattern}" if pattern else ""))
    for f in sorted(files):
        print(f" - {os.path.basename(f)}")
    return True


def extract_headers(filepath):
    """Extract and display markdown headers from a file"""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False
    with open(filepath, "r") as f:
        content = f.read()
    headers = []
    for line in content.split("\n"):
        if line.strip().startswith("#"):
            headers.append(line.strip())
    if not headers:
        print(f"No headers found in {filepath}")
        return False
    print(f"Headers in {filepath}:")
    for header in headers:
        print(f" - {header}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Campaign Tools for D&D Management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup all campaign data")

    # Create template command
    template_parser = subparsers.add_parser("create", help="Create a new template file")
    template_parser.add_argument("type", choices=["location", "npc", "item"], help="Template type")
    template_parser.add_argument("name", help="Name for the new entity")

    # List files command
    list_parser = subparsers.add_parser("list", help="List files in campaign directories")
    list_parser.add_argument(
        "--dir", choices=["core", "gen", "raw"], default="core", help="Directory to list (default: core)"
    )
    list_parser.add_argument("--pattern", help='File pattern to match (e.g., "*.md")')

    # Show outline command
    outline_parser = subparsers.add_parser("outline", help="Show outline of a markdown file")
    outline_parser.add_argument("file", help="File to show outline for")

    # Parse arguments
    args = parser.parse_args()

    # Ensure directories exist
    ensure_directories()

    # Execute appropriate command
    if args.command == "backup":
        backup_campaign()
    elif args.command == "create":
        create_template(args.type, args.name)
    elif args.command == "list":
        # Map directory choice to actual path
        dir_map = {"core": CORE_DOCS, "gen": GEN_DOCS, "raw": RAW_DATA}
        list_files(dir_map[args.dir], args.pattern)
    elif args.command == "outline":
        extract_headers(args.file)
    else:
        parser.print_help()