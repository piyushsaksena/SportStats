"""Data Cleaning, Normalization and Sanitization Module for SportStats.

Implements rules specified in Section 8.4 and Part 15 (Security):
- Country normalization to ISO3
- Date parsing and UTC normalization
- Participant name alias normalization
- Formula injection detection
"""

from datetime import date, datetime, timezone
from typing import Dict, Optional

# Pre-compiled mapping from common country names, nationalities, and variations to ISO3 codes
COUNTRY_NAME_TO_ISO3: Dict[str, str] = {
    # India
    "india": "IND",
    "ind": "IND",
    "republic of india": "IND",
    # United States
    "united states": "USA",
    "usa": "USA",
    "united states of america": "USA",
    "us": "USA",
    # United Kingdom / Great Britain / England
    "great britain": "GBR",
    "gbr": "GBR",
    "united kingdom": "GBR",
    "uk": "GBR",
    "england": "GBR",
    "scotland": "GBR",
    "wales": "GBR",
    # Australia
    "australia": "AUS",
    "aus": "AUS",
    # France
    "france": "FRA",
    "fra": "FRA",
    # Germany
    "germany": "GER",
    "ger": "GER",
    "deutschland": "GER",
    # Japan
    "japan": "JPN",
    "jpn": "JPN",
    # China
    "china": "CHN",
    "chn": "CHN",
    "people's republic of china": "CHN",
    # Brazil
    "brazil": "BRA",
    "brasil": "BRA",
    "bra": "BRA",
    # Spain
    "spain": "ESP",
    "esp": "ESP",
    # Argentina
    "argentina": "ARG",
    "arg": "ARG",
    # Qatar
    "qatar": "QAT",
    "qat": "QAT",
    # Russia
    "russia": "RUS",
    "rus": "RUS",
    # Denmark
    "denmark": "DNK",
    "dnk": "DNK",
    # Iran
    "iran": "IRN",
    "irn": "IRN",
    # South Korea
    "south korea": "KOR",
    "korea": "KOR",
    "kor": "KOR",
    # Pakistan
    "pakistan": "PAK",
    "pak": "PAK",
    # New Zealand
    "new zealand": "NZL",
    "nzl": "NZL",
    # Sri Lanka
    "sri lanka": "SRI",
    "sri": "SRI",
    # South Africa
    "south africa": "RSA",
    "rsa": "RSA",
    # Canada
    "canada": "CAN",
    "can": "CAN",
    # Italy
    "italy": "ITA",
    "ita": "ITA",
    # Serbia
    "serbia": "SRB",
    "srb": "SRB",
    # Indonesia
    "indonesia": "INA",
    "ina": "INA",
    # Malaysia
    "malaysia": "MAS",
    "mas": "MAS",
    # Thailand
    "thailand": "THA",
    "tha": "THA",
    # Kenya
    "kenya": "KEN",
    "ken": "KEN",
    # Jamaica
    "jamaica": "JAM",
    "jam": "JAM",
}

# Participant alias mapping (normalising team/athlete names)
PARTICIPANT_ALIASES: Dict[str, str] = {
    "team india": "India",
    "indian cricket team": "India",
    "indian national team": "India",
    "team usa": "United States",
    "usa men's team": "United States",
    "aus cricket": "Australia",
    "the socceroos": "Australia",
    "selecao": "Brazil",
    "la albiceleste": "Argentina",
    "les bleus": "France",
}

# Characters that trigger formula injection warnings in spreadsheet viewers
FORMULA_INJECTION_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def has_formula_injection(value: str) -> bool:
    """Detect whether a string value starts with potentially executable spreadsheet formula characters.

    Part 15 security requirement: scan CSVs for formula injection (cells beginning with =, +, -, @).
    """
    if not value or not isinstance(value, str):
        return False
    stripped = value.strip()
    if not stripped:
        return False
    return stripped.startswith(FORMULA_INJECTION_PREFIXES)


def normalize_country_iso3(value: Optional[str]) -> Optional[str]:
    """Normalize raw country name or code into an ISO3 uppercase code.

    Returns ISO3 string if resolved, or None if unknown.
    """
    if not value or not isinstance(value, str):
        return None
    val = value.strip()
    if not val:
        return None
    # If already 3 uppercase letters and directly in mapping
    val_lower = val.lower()
    if val_lower in COUNTRY_NAME_TO_ISO3:
        return COUNTRY_NAME_TO_ISO3[val_lower]
    # Check if exactly 3 alphabetic characters (candidate ISO3)
    if len(val) == 3 and val.isalpha():
        return val.upper()
    return None


def normalize_participant_name(name: Optional[str]) -> Optional[str]:
    """Normalize participant names using alias dictionary and whitespace stripping."""
    if not name or not isinstance(name, str):
        return None
    cleaned = name.strip()
    cleaned_lower = cleaned.lower()
    return PARTICIPANT_ALIASES.get(cleaned_lower, cleaned)


def parse_iso_date(value: Optional[str]) -> Optional[date]:
    """Parse date string into a standard date object.

    Accepts ISO 8601 formats: YYYY-MM-DD or YYYY/MM/DD.
    """
    if not value or not isinstance(value, str):
        return None
    val = value.strip()
    if not val:
        return None

    # Try standard YYYY-MM-DD
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(val, fmt).date()
        except ValueError:
            continue
    return None


def parse_iso_datetime_utc(value: Optional[str]) -> Optional[datetime]:
    """Parse datetime string and ensure UTC timezone."""
    if not value or not isinstance(value, str):
        return None
    val = value.strip()
    if not val:
        return None

    for fmt in (
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(val, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None
