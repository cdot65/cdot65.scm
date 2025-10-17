# Contributing to cdot65.scm

Thank you for your interest in contributing to the cdot65.scm Ansible collection!

## Getting Started

1. Fork the repository and clone your fork
2. Set up the development environment:
   ```bash
   make dev-setup
   ```

## Development Workflow

### 1. Install pre-commit hooks

We use pre-commit to enforce code quality and consistency:

```bash
pip install pre-commit
pre-commit install
```

### 2. Create a Feature Branch

Always work in a feature branch, never directly on main:

```bash
git checkout -b feature/your-feature-name
```

### 3. Development Cycle

1. Make your changes
2. Run linting and formatting:
   ```bash
   make lint-check
   ```  
3. Fix any issues automatically:
   ```bash
   make lint-fix
   ```
4. Run tests to ensure your changes work:
   ```bash
   make test
   ```
5. Build and install locally to test end-to-end:
   ```bash
   make all
   ```

### 4. Submit a Pull Request

1. Push your feature branch to your fork
2. Create a pull request against the main repository's main branch
3. Ensure the PR description clearly explains the changes and motivation

## Code Standards

### Python Code

All Python code should:

1. Follow PEP 8 style guidelines
2. Use type hints where appropriate
3. Include Google-style docstrings for all functions and classes
4. Be formatted with Black (line length 120)
5. Have imports sorted with isort
6. Pass all ruff linting rules configured in pyproject.toml

### Ansible Modules

All Ansible modules should:

1. Be idempotent (running multiple times produces the same result)
2. Support check mode
3. Include comprehensive documentation with examples
4. Follow the pattern established in existing modules
5. Handle errors gracefully with informative messages
6. Properly manage sensitive data with no_log

### YAML Files

All YAML files should:

1. Use 2-space indentation
2. Pass ansible-lint checks
3. Use consistent naming conventions

## Testing

We use several types of tests:

1. **Sanity tests**: Ensure code meets Ansible standards
   ```bash
   make sanity
   ```
   
2. **Unit tests**: Test individual functions/classes
   ```bash
   make unit-test
   ```
   
3. **Integration tests**: Test modules against real SCM (requires credentials)
   ```bash
   make integration-test
   ```

## Documentation

When adding new features:

1. Update module documentation (in the module itself)
2. Add examples to the examples/ directory
3. Update README.md if necessary
4. Update CLAUDE.md to reflect the changes

## Security

- NEVER commit credentials to source control
- Always use Ansible Vault for secrets in examples
- Mark sensitive parameters with no_log: true

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.