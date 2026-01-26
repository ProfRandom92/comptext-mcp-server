# Contributing to CompText MCP Server

First off, thank you for considering contributing to CompText MCP Server! 🎉

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## 📜 Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue tracker as you might find that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if relevant**
- **Specify your environment** (OS, Python version, MCP version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **A clear and descriptive title**
- **A detailed description of the proposed functionality**
- **Examples of how the feature would be used**
- **Why this enhancement would be useful**

### Your First Code Contribution

Unsure where to begin? Look for issues labeled:
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `documentation` - Improvements to docs

## 🛠️ Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Optional: uv for faster package management

### Setup Steps

```bash
# Fork the repository on GitHub

# Clone your fork
git clone https://github.com/YOUR_USERNAME/comptext-mcp-server.git
cd comptext-mcp-server

# Add upstream remote
git remote add upstream https://github.com/ProfRandom92/comptext-mcp-server.git

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## 🔄 Pull Request Process

### Branch Naming

Use descriptive branch names:
- `feature/add-websocket-support`
- `bugfix/fix-compiler-crash`
- `docs/update-api-documentation`
- `refactor/improve-error-handling`

### Commit Messages

Follow conventional commits:
- `feat: add WebSocket support for real-time compilation`
- `fix: resolve crash when compiling empty input`
- `docs: update API documentation with examples`
- `refactor: simplify error handling logic`
- `test: add tests for NL compiler edge cases`
- `chore: update dependencies to latest versions`

### Pull Request Steps

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, documented code
   - Add tests for new functionality
   - Update documentation

3. **Run quality checks**
   ```bash
   # Format code
   black src/ tests/
   isort src/ tests/
   
   # Type checking
   mypy src/
   
   # Linting
   flake8 src/ tests/
   
   # Tests
   pytest tests/ -v --cov
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**
   - Fill out the PR template completely
   - Link related issues
   - Request review from maintainers

### PR Review Process

- Maintainers will review your PR within 2-3 business days
- Address any requested changes
- Once approved, a maintainer will merge your PR

## 💻 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://github.com/psf/black) for code formatting (line length: 127)
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use type hints for all functions

### Code Quality

```python
# Good: Clear, documented, typed
def compile_nl_to_dsl(
    text: str,
    audience: str = "dev",
    confidence_threshold: float = 0.65
) -> dict[str, Any]:
    """Compile natural language to CompText DSL.
    
    Args:
        text: Natural language input
        audience: Target audience (dev/audit/exec)
        confidence_threshold: Minimum confidence score
        
    Returns:
        Compiled DSL with confidence score
        
    Raises:
        ValueError: If text is empty
    """
    if not text:
        raise ValueError("Input text cannot be empty")
    
    # Implementation...
    return {"dsl": compiled, "confidence": 0.85}
```

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors appropriately

```python
try:
    result = compile_text(input_text)
except ValueError as e:
    logger.error(f"Invalid input: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error during compilation: {e}")
    raise CompilerError("Compilation failed") from e
```

## 🧪 Testing Guidelines

### Writing Tests

- Write tests for all new features
- Maintain >80% code coverage
- Use descriptive test names

```python
def test_nl_compiler_handles_empty_input():
    """Test that compiler raises ValueError for empty input."""
    with pytest.raises(ValueError, match="Input text cannot be empty"):
        compile_nl_to_dsl("")

def test_nl_compiler_returns_high_confidence_for_clear_intent():
    """Test compiler confidence for unambiguous requests."""
    result = compile_nl_to_dsl("Review this code for bugs")
    assert result["confidence"] >= 0.7
    assert "code.review" in result["dsl"]
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_compiler.py -v

# Run with coverage
pytest tests/ --cov=src/comptext_mcp --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

## 📚 Documentation

### Code Documentation

- Document all public APIs
- Use Google-style docstrings
- Include examples in docstrings

### README Updates

- Update README.md for new features
- Add examples for new functionality
- Keep documentation accurate and up-to-date

### API Documentation

- Update docs/API.md for API changes
- Document all endpoints and parameters
- Provide curl examples

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Celebrated in our community

## ❓ Questions?

- 💬 Open a [Discussion](https://github.com/ProfRandom92/comptext-mcp-server/discussions)
- 📧 Email: 159939812+ProfRandom92@users.noreply.github.com

Thank you for contributing! 🙏
