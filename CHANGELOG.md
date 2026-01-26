# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Redis caching for distributed deployments
- Batch compilation support
- Custom bundle creation API
- VSCode extension
- Web playground for testing

## [2.0.0] - 2026-01-26

### 🎉 Major Release: Natural Language Compiler

This is a major milestone release introducing the CompText Natural Language Compiler,
transforming the repository into a production-ready, enterprise-grade system.

### Added

#### Core Compiler (New!)
- **Natural Language to CompText Compiler** with bundle-first architecture
- **11 Specialized Bundles** covering code, security, docs, devops, ML workflows
- **3 Audience Profiles** (dev/audit/exec) with tailored configurations
- **Confidence Scoring** with automatic clarification questions for ambiguous inputs
- **Deterministic Compilation** ensuring same input → same output
- **Keyword-based Matching** with domain bonuses for accurate bundle selection
- **Canonical DSL Format** with profile → bundles → deltas ordering
- **Bundle Registry** stored in YAML with validation

#### Testing & Quality
- **38 Comprehensive Tests** with 98% code coverage
- Test suite for registry, matcher, canonicalizer, and compiler
- Edge case tests (empty input, unicode, special characters)
- Performance tests (24ms average per compilation)
- Integration tests with golden prompts
- Pytest configuration with coverage reporting

#### Documentation
- **Enhanced README** with usage examples and architecture diagrams
- **ROADMAP.md** outlining future development plans
- **CONTRIBUTORS.md** for community recognition
- **CODEOWNERS** file for code ownership
- **Comprehensive docstrings** for all compiler modules
- **Enhanced COMPILER_SPEC.md** with detailed examples and scoring rules
- **Architecture diagrams** showing system overview and compilation pipeline

#### CI/CD & Automation
- **Quality Workflow** with black, isort, flake8, mypy checks
- **Multi-Python Version Testing** (3.10, 3.11, 3.12)
- **Security Scanning** with bandit and safety
- **Coverage Reporting** with Codecov integration
- **Automated Summary Reports** in GitHub Actions
- **Code Formatting Enforcement** via CI

#### Code Quality
- **100% Black Formatted** code (line-length=127)
- **Import Sorting** with isort (black profile)
- **Comprehensive Type Hints** throughout compiler
- **Professional Docstrings** with examples and parameter descriptions
- **Fixed setup.py** to handle recursive requirements

### Changed
- **Updated to v2.0.0** across all package files
- **MCP Server** now includes 8 tools (added `nl_to_comptext`)
- **Enhanced .gitignore** with comprehensive patterns
- **Improved CI workflow** with better dependency management
- **README badges** updated with coverage and CI status

### Technical Improvements
- **98% Test Coverage** for compiler modules
- **Zero External API Dependencies** for compilation (pure YAML-based)
- **Sub-50ms Compilation** for typical inputs
- **Type-safe** dataclasses for all data structures
- **Immutable** registry and bundle objects for thread safety

### Performance
- Average compilation time: **24ms** (includes YAML loading)
- Throughput: **~40 compilations/second** on standard hardware
- Memory footprint: **< 50MB** for full registry
- Zero network latency (local YAML storage)

## [1.0.0] - 2024-12-04

### Added
- Initial release of CompText MCP Server
- MCP Server with 7 tools
  - list_modules
  - get_module
  - get_command
  - search
  - get_by_tag
  - get_by_type
  - get_statistics
- REST API with 8 endpoints
- Multi-platform support (Claude, Perplexity, Cursor, etc.)
- Docker support with Dockerfile and docker-compose
- Railway deployment configuration
- Comprehensive documentation
- Setup scripts for macOS/Linux and Windows
- LRU caching for performance
- Error handling and logging
- Type hints throughout codebase

### Features

#### MCP Tools
- Full integration with Model Context Protocol
- Async/await support
- Rich formatted output
- Error handling with custom exceptions

#### REST API
- FastAPI-based HTTP interface
- Swagger/OpenAPI documentation
- CORS support
- Health check endpoint
- Cache management endpoint

#### Deployment
- Docker container support
- Railway one-click deploy
- ngrok integration for development
- Environment-based configuration

#### Documentation
- Comprehensive README
- Quick start guide
- API reference
- Deployment guide
- Platform-specific setup instructions

### Security
- Environment variable-based secrets
- No hardcoded credentials
- Secure Notion API integration

### Performance
- LRU caching for frequent queries
- Optimized database queries
- Async operations support

## [0.1.0] - 2024-11-01

### Added
- Initial prototype
- Basic Notion API integration
- Simple MCP server implementation

---

## Version History

- **1.0.0**: Production release with full features
- **0.1.0**: Initial prototype

## Upgrade Guide

### From 0.x to 1.0

No breaking changes. Simply:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Future Plans

- [ ] GraphQL API support
- [ ] WebSocket for real-time updates
- [ ] Advanced caching strategies
- [ ] Metrics and monitoring
- [ ] Multi-database support
- [ ] Plugin system
- [ ] Admin dashboard
