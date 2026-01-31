"""Shared constants for CompText MCP Server"""

# Module mapping - Single source of truth
MODULE_MAP = {
    "A": "Modul A: Allgemeine Befehle",
    "B": "Modul B: Programmierung",
    "C": "Modul C: Visualisierung",
    "D": "Modul D: KI-Steuerung",
    "E": "Modul E: Datenanalyse & ML",
    "F": "Modul F: Dokumentation",
    "G": "Modul G: Testing & QA",
    "H": "Modul H: Database & Data Modeling",
    "I": "Modul I: Security & Compliance",
    "J": "Modul J: DevOps & Deployment",
    "K": "Modul K: Frontend & UI",
    "L": "Modul L: Data Pipelines & ETL",
    "M": "Modul M: MCP Integration",
}

# API Configuration
DEFAULT_MAX_RESULTS = 20
MAX_SEARCH_RESULTS = 100

# Cache Configuration
CACHE_SIZE = 128
CACHE_TTL = 3600  # 1 hour in seconds

# Notion API Configuration
DEFAULT_DATABASE_ID = "0e038c9b52c5466694dbac288280dd93"

# Local Codex Configuration
DEFAULT_DATA_PATH = "data/codex.json"

# Data Source Configuration
# Valid values: "notion" or "local"
DATA_SOURCE = "local"  # Default to local JSON file

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
BACKOFF_FACTOR = 2
