"""CompText Natural Language Compiler.

This package implements the NL→CompText compiler with bundle-first architecture.

Main components:
- registry: Bundle and profile data structures and loading
- matcher: Keyword-based bundle matching from natural language
- canonicalize: DSL output rendering in canonical format
- nl_to_comptext: Main compilation entry point

Usage:
    >>> from comptext_mcp.compiler import compile_nl_to_comptext
    >>> result = compile_nl_to_comptext("review this code for best practices")
    >>> print(result)
    dsl:
    use:profile.dev.v1
    use:code.review.v1

    confidence: 0.85
    clarification: null
"""

__all__ = [
    "compile_nl_to_comptext",
    "load_registry",
    "Registry",
    "Bundle",
    "Profile",
    "MatchResult",
]

from .matcher import MatchResult
from .nl_to_comptext import compile_nl_to_comptext
from .registry import Bundle, Profile, Registry, load_registry
