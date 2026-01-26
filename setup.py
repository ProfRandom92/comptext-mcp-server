"""Setup script for CompText MCP Server."""
from setuptools import setup, find_packages
import os

# Read README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements(filename):
    """Read requirements from a file, handling -r includes.

    Args:
        filename: Path to requirements file

    Returns:
        List of requirement strings
    """
    requirements = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Handle -r includes
            if line.startswith("-r "):
                include_file = line.split(" ", 1)[1]
                requirements.extend(read_requirements(include_file))
            else:
                requirements.append(line)
    return requirements

base_requirements = read_requirements("requirements.txt")
# Read dev and rest requirements directly without includes to avoid duplicates
dev_requirements = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.7.0",
    "flake8>=6.1.0",
    "mypy>=1.5.0",
]
rest_requirements = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
]

setup(
    name="comptext-mcp-server",
    version="2.0.0",
    author="ProfRandom92",
    author_email="159939812+ProfRandom92@users.noreply.github.com",
    description="Token-efficient Domain-Specific Language for LLM interactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ProfRandom92/comptext-mcp-server",
    project_urls={
        "Bug Tracker": "https://github.com/ProfRandom92/comptext-mcp-server/issues",
        "Documentation": "https://www.notion.so/0d571dc857144b199243ea951d60cef6",
        "Source Code": "https://github.com/ProfRandom92/comptext-mcp-server",
    },
    package_dir={"" : "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=base_requirements,
    extras_require={
        "dev": dev_requirements,
        "rest": rest_requirements,
        "all": dev_requirements + rest_requirements,
    },
    entry_points={
        "console_scripts": [
            "comptext-mcp=comptext_mcp.server:main",
        ],
    },
)
