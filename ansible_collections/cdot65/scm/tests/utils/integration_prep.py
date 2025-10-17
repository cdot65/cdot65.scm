#!/usr/bin/env python

# Utility script to prepare the environment for ansible-test integration tests
# Based on amazon.aws collection structure

import os
import shutil
import sys
from pathlib import Path

# Main project directory
base_dir = Path(__file__).parent.parent.parent.absolute()

# Get the Ansible collections path from environment
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

# Create a symlink to the collection source directory
os.symlink(base_dir, collection_path)

# Check if required environment variables are set
required_env_vars = ["SCM_API_KEY", "SCM_API_URL"]
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]

if missing_vars:
    print(f"Warning: The following environment variables are not set: {', '.join(missing_vars)}")
    print("Integration tests may fail without proper credentials.")

print(f"Integration test environment prepared at {collection_path}")
print("Note: For integration tests to work correctly, make sure to set SCM_API_KEY and SCM_API_URL environment variables.")
