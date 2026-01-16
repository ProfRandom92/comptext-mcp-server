import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
from typing import Optional

# Add src to path to enable direct imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the actual compiler
from comptext_mcp.compiler.nl_to_comptext import compile_nl_to_comptext
from comptext_mcp.compiler.registry import load_registry

# FastAPI App initialisieren
app = FastAPI(
    title="CompText MCP Server",
    version="3.5.2",
    description="HTTP wrapper for CompText Natural Language to DSL compiler"
)

# Load registry at startup
try:
    registry = load_registry()
except Exception as e:
    registry = None
    print(f"Warning: Could not load registry: {e}")


class CompileRequest(BaseModel):
    text: str = Field(..., description="Natural language request to compile to CompText")
    audience: str = Field(default="dev", description="Target audience: dev, audit, or exec")
    mode: str = Field(default="bundle_only", description="Compilation mode: bundle_only or allow_inline_fallback")
    return_mode: str = Field(default="dsl_plus_confidence", description="Return format: dsl_only, dsl_plus_confidence, or dsl_plus_explanation")


class CompileResponse(BaseModel):
    dsl: str
    confidence: Optional[float] = None
    clarification: Optional[str] = None
    explanation: Optional[str] = None


@app.get("/")
async def root():
    """Server Status Endpoint"""
    return {
        "status": "CompText MCP Server running",
        "version": "3.5.2",
        "description": "Natural Language to CompText DSL compiler",
        "registry_loaded": registry is not None,
        "endpoints": {
            "health": "/health",
            "compile": "/compile (POST)",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Health Check Endpoint"""
    return {
        "status": "healthy",
        "registry_loaded": registry is not None
    }


@app.post("/compile", response_model=dict)
async def compile_nl_to_dsl(request: CompileRequest):
    """
    Compile natural language to canonical CompText DSL

    This endpoint converts natural language requests into CompText DSL
    using a bundle-based matching system with confidence scoring.

    Returns:
        - dsl: The compiled CompText DSL code
        - confidence: Confidence score (0-1) if requested
        - clarification: Question to ask user if confidence is low
        - explanation: Explanation of the match if requested
    """
    if registry is None:
        raise HTTPException(status_code=500, detail="Registry not loaded")

    try:
        result = compile_nl_to_comptext(
            text=request.text,
            audience=request.audience,
            mode=request.mode,
            return_mode=request.return_mode
        )

        # Parse the result string
        response = {}

        # Split into lines for parsing
        lines = result.split("\n")

        # Extract DSL block
        if lines[0].startswith("dsl:"):
            # Find where DSL ends (empty line or confidence/clarification/explanation)
            dsl_lines = []
            i = 1
            while i < len(lines):
                line = lines[i]
                if line.strip() == "" or line.startswith(("confidence:", "clarification:", "explanation:")):
                    break
                dsl_lines.append(line)
                i += 1

            response["dsl"] = "\n".join(dsl_lines).strip()

            # Parse remaining fields
            for line in lines[i:]:
                line = line.strip()
                if line.startswith("confidence:"):
                    conf_str = line.replace("confidence:", "").strip()
                    try:
                        response["confidence"] = float(conf_str)
                    except ValueError:
                        pass
                elif line.startswith("clarification:"):
                    clar = line.replace("clarification:", "").strip()
                    if clar and clar != "null":
                        response["clarification"] = clar
                elif line.startswith("explanation:"):
                    expl = line.replace("explanation:", "").strip()
                    if expl:
                        response["explanation"] = expl
        else:
            # Fallback: treat entire result as clarification
            response["dsl"] = ""
            response["clarification"] = result
            response["confidence"] = 0.0

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compilation failed: {str(e)}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
