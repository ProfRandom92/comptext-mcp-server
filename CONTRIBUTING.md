# Contributing to CompText MCP Server

First off, thank you for considering contributing to CompText MCP Server! 🎉

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues. When you create a bug report, include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Provide specific examples
- Describe the behavior you observed and what you expected
- Include logs and error messages
- Mention your environment (OS, Python version, platform)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- Use a clear and descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful
- List any alternative solutions you've considered

### Pull Requests

1. Fork the repo and create your branch from `main`
2. Install development dependencies: `pip install -r requirements-dev.txt`
3. Set up pre-commit hooks: `pre-commit install`
4. Make your changes
5. Add tests for your changes
6. Ensure all tests pass: `pytest tests/ -v`
7. Format your code: `black src/ tests/`
8. Lint your code: `flake8 src/ tests/`
9. Update documentation if needed
10. Commit your changes with a descriptive message
11. Push to your fork and submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/comptext-mcp-server.git
cd comptext-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Configure environment
cp .env.example .env
# Add your NOTION_API_TOKEN

# Run tests
pytest tests/ -v
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for code formatting
- Maximum line length: 127 characters
- Use type hints where applicable
- Write docstrings for all public functions/classes

### Example

```python
def get_module_by_name(module_name: str) -> List[Dict[str, Any]]:
    """Load all entries of a specific module.
    
    Args:
        module_name: Name of the module to load
        
    Returns:
        List of module entries
        
    Raises:
        NotionClientError: If API request fails
    """
    # Implementation
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new search filter for tags
fix: resolve pagination issue in list_modules
docs: update API documentation
test: add tests for search functionality
refactor: improve error handling in notion_client
chore: update dependencies
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/comptext_mcp --cov-report=html

# Run specific test
pytest tests/test_suite.py::TestNotionClient::test_get_all_modules -v
```

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

```python
def test_search_codex_with_valid_query():
    # Arrange
    query = "docker"
    max_results = 5
    
    # Act
    results = search_codex(query, max_results)
    
    # Assert
    assert isinstance(results, list)
    assert len(results) <= max_results
```

## Documentation

- Update README.md for user-facing changes
- Update docs/ for detailed documentation
- Add docstrings to new functions/classes
- Include examples in documentation

## Release Process

1. Update version in `src/comptext_mcp/__init__.py`
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. Tag the release: `git tag -a v1.1.0 -m "Release v1.1.0"`
5. Push tags: `git push origin v1.1.0`

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
