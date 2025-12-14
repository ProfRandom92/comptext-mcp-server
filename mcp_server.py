"""Simple FastAPI Server for Render.com Deployment"""
import os
from fastapi import FastAPI
import uvicorn

# FastAPI App initialisieren
app = FastAPI(
    title="CompText MCP Server",
    version="1.0.0",
    description="Production-ready MCP server for CompText DSL"
)


@app.get("/")
async def root():
    """Server Status Endpoint"""
    return {
        "status": "CompText MCP Server running",
        "version": "1.0.0",
        "message": "For full API functionality, use rest_api_wrapper.py",
        "mcp_protocol": "Use stdio mode for MCP client integration",
        "endpoints": {
            "health": "/health",
            "info": "/"
        }
    }


@app.get("/health")
async def health():
    """Health Check Endpoint for Render.com"""
    return {
        "status": "healthy",
        "service": "comptext-mcp-server",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
