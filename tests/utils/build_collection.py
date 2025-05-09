#!/usr/bin/env python

# Utility script to build the collection for testing purposes
# Based on amazon.aws collection

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Main project directory
base_dir = Path(__file__).parent.parent.parent.absolute()

# Build the collection
try:
    proc = subprocess.run(
        ["ansible-galaxy", "collection", "build", "--force"],
        check=True,
        capture_output=True,
        cwd=base_dir,
    )
    print(proc.stdout.decode())
except subprocess.CalledProcessError as e:
    print(f"Error building collection: {e}")
    print(f"stdout: {e.stdout.decode()}")
    print(f"stderr: {e.stderr.decode()}")
    sys.exit(1)

# Find the built .tar.gz file
for file in os.listdir(base_dir):
    if file.startswith("cdot65-scm-") and file.endswith(".tar.gz"):
        build_file = os.path.join(base_dir, file)
        print(f"Found built collection: {build_file}")
        break
else:
    print("Could not find built collection archive")
    sys.exit(1)

print("Collection built successfully")
