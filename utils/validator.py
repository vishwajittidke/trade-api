import re
from config import ALLOWED_SECTORS


def validate_sector(sector):
    if not sector or not isinstance(sector, str):
        raise ValueError("Sector name is required")

    sector = sector.lower().strip()

    # basic sanitization - only allow letters, spaces, hyphens
    if not re.match(r"^[a-z\s\-]+$", sector):
        raise ValueError("Sector name contains invalid characters")

    if sector not in ALLOWED_SECTORS:
        allowed = ", ".join(sorted(ALLOWED_SECTORS))
        raise ValueError(f"Unknown sector '{sector}'. Available: {allowed}")

    return sector


def validate_markdown(text):
    """check if the AI output has all the sections we expect"""
    if not text:
        return False

    required = ["## Summary", "## Key Trends", "## Trade Opportunities",
                 "## Risks", "## Recommendation"]
    return all(section in text for section in required)
