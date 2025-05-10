#!/bin/bash
# Fix C408 warnings in module_utils

set -e

# Fix the RET504 warnings (unnecessary assignment before return)
find plugins/module_utils -name "*.py" -exec sed -i '' 's/client = ScmClient(/return ScmClient(/g' {} \;
find plugins/module_utils -name "*.py" -exec sed -i '' 's/client = SCMClient(/return SCMClient(/g' {} \;
find plugins/module_utils -name "*.py" -exec sed -i '' 's/return client/)/g' {} \;

# Run the formatters to clean up any issues
poetry run black plugins/module_utils
poetry run isort plugins/module_utils

echo "Fixed common linting issues in module_utils"