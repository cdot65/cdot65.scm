#!/usr/bin/env python

# Utility script to prepare the environment for ansible-test sanity checks
# Based on amazon.aws collection structure

import os
import subprocess
import sys
from pathlib import Path

# Main project directory
base_dir = Path(__file__).parent.parent.parent.absolute()

# Run ansible-galaxy collection install
try:
    env = os.environ.copy()
    env["ANSIBLE_COLLECTIONS_PATH"] = str(base_dir)

    proc = subprocess.run(
        ["ansible-galaxy", "collection", "build", "--force"],
        check=True,
        capture_output=True,
        cwd=base_dir,
        env=env,
    )
    print(proc.stdout.decode())

    # Find the built .tar.gz file
    collection_file = None
    for file in os.listdir(base_dir):
        if file.startswith("cdot65-scm-") and file.endswith(".tar.gz"):
            collection_file = os.path.join(base_dir, file)
            break

    if not collection_file:
        print("Could not find built collection archive")
        sys.exit(1)

    # Install the collection to a temporary directory
    proc = subprocess.run(
        ["ansible-galaxy", "collection", "install", "-f", collection_file],
        check=True,
        capture_output=True,
        cwd=base_dir,
        env=env,
    )
    print(proc.stdout.decode())
except subprocess.CalledProcessError as e:
    print(f"Error preparing environment: {e}")
    print(f"stdout: {e.stdout.decode()}")
    print(f"stderr: {e.stderr.decode()}")
    sys.exit(1)

print("Sanity test environment prepared successfully")
