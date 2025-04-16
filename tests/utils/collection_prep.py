#!/usr/bin/env python

# Utility script to prepare the collection for testing
# Based on amazon.aws collection structure

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Main project directory
base_dir = Path(__file__).parent.parent.parent.absolute()

# Get the Ansible collections path from environment or set default
if "ANSIBLE_COLLECTIONS_PATH" not in os.environ:
    print("ANSIBLE_COLLECTIONS_PATH environment variable is not set, using default")
    sys.exit(1)

collections_path = Path(os.environ["ANSIBLE_COLLECTIONS_PATH"])
namespace_path = collections_path / "ansible_collections" / "cdot65"
collection_path = namespace_path / "scm"

# Create the collections directory structure
os.makedirs(namespace_path, exist_ok=True)

# If the collection directory already exists, remove it
if collection_path.exists():
    shutil.rmtree(collection_path)

# Copy the collection directory
shutil.copytree(base_dir / "plugins", collection_path / "plugins")
shutil.copytree(base_dir / "docs", collection_path / "docs", dirs_exist_ok=True)
if (base_dir / "meta").exists():
    shutil.copytree(base_dir / "meta", collection_path / "meta", dirs_exist_ok=True)

# Create symlinks for the tests
if not (collection_path / "tests").exists():
    os.symlink(base_dir / "tests", collection_path / "tests")

print(f"Collection prepared at {collection_path}")
