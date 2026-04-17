"""
Sector label → Dhan index name mapping.

Used to look up the security_id for each sector index in the
Dhan scrip master CSV at scan time.
"""

SECTOR_INDICES: dict[str, str] = {
    "IT":             "NIFTY IT",
    "Bank":           "NIFTY BANK",
    "Financial Svcs": "NIFTY FINANCIAL SERVICES",
    "Auto":           "NIFTY AUTO",
    "Pharma":         "NIFTY PHARMA",
    "FMCG":           "NIFTY FMCG",
    "Metal":          "NIFTY METAL",
    "Energy":         "NIFTY ENERGY",
    "Realty":         "NIFTY REALTY",
    "Infra":          "NIFTY INFRA",
    "Media":          "NIFTY MEDIA",
    "PSU Bank":       "NIFTY PSU BANK",
}
