# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-26

### 🚀 Added
- **Mobile-First Transformation** - Complete mobile agent support
- **iOS Integration** - Siri Shortcuts and iOS app support
- **Android Integration** - Tasker automation support
- **Telegram Bot** - Mobile messaging interface
- **Mobile Performance Metrics** - Real device benchmarks
- **Offline Capability** - Local DSL processing
- **Battery Optimization** - Power-efficient processing
- **Professional README** - Mobile-first documentation

### ⚡ Changed
- **README.md** - Completely rewritten with mobile-first focus
- **Performance** - Optimized for mobile devices (<100ms latency)
- **Memory Footprint** - Reduced to <50MB for mobile

### 📝 Documentation
- Mobile-first README with iOS/Android examples
- Performance benchmarks for mobile devices
- Battery and bandwidth optimization guides
- Integration examples for Telegram, WhatsApp, SMS

### 🔧 Configuration
- Mobile environment configuration (`.env.mobile.example`)
- Edge computing optimizations
- Offline mode support

## [1.0.0] - 2025-12-04

### 🎉 Initial Release

#### Core Features
- **Natural Language Compiler** - Convert NL to CompText DSL
- **Bundle-First Architecture** - Pre-optimized command bundles
- **13 Specialized Modules** - A-M covering all domains
- **MCP Server Implementation** - Full Model Context Protocol support
- **REST API Wrapper** - FastAPI-based HTTP interface
- **Notion Integration** - Codex data management
- **Audience Profiles** - dev/audit/exec tailored output

#### Tools Available
- `list_modules` - List all CompText modules
- `get_module` - Get specific module details
- `search` - Search codex by keywords
- `get_command` - Get command documentation
- `get_by_tag` - Filter by tags
- `get_by_type` - Filter by type
- `get_statistics` - View codex statistics
- `nl_to_comptext` - Compile NL to DSL

#### Quality & Testing
- Comprehensive test suite with pytest
- Type hints throughout codebase
- Code quality tools (black, isort, flake8, mypy)
- CI/CD pipeline with GitHub Actions
- Docker support for containerization

#### Documentation
- Complete README with examples
- API documentation
- Quick start guide
- FAQ section
- Deployment guides

#### Deployment
- Docker and docker-compose support
- Render.com auto-deployment
- Railway.app configuration
- Health check endpoints
- Metrics and monitoring

---

## [Unreleased]

### Planned Features
- WebSocket support for real-time compilation
- Plugin system for custom modules
- Multi-language DSL support
- Visual DSL editor
- ML-based bundle optimization
- Distributed codex synchronization
- Native mobile apps (iOS & Android)

---

## Release Guidelines

### Version Numbering
- **Major (X.0.0)** - Breaking changes, major features
- **Minor (0.X.0)** - New features, backwards compatible
- **Patch (0.0.X)** - Bug fixes, small improvements

### Release Process
1. Update version in `pyproject.toml` and `src/comptext_mcp/__init__.py`
2. Update CHANGELOG.md with release notes
3. Create git tag: `git tag -a v2.0.0 -m "Release v2.0.0"`
4. Push tag: `git push origin v2.0.0`
5. GitHub Actions automatically builds and publishes

---

For full commit history, see: https://github.com/ProfRandom92/comptext-mcp-server/commits/main
