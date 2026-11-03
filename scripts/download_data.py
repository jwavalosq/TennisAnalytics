"""Download the source files used by this project.

Run from the project root:
    python scripts/download_data.py

Original repo files come from jwavalosq/TennisAnalytics on GitHub.
The Sackmann supplement comes from the Aneeshers archive mirror, because
the original JeffSackmann tennis_atp and tennis_wta repos returned 404
when checked on 2026-11-03. The archive states it mirrors Sackmann data
and asks users to attribute Jeff Sackmann. See data/raw/PROVENANCE.md.
"""
import os
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")

ORIGINAL = {
    "Match.csv": "https://raw.githubusercontent.com/jwavalosq/TennisAnalytics/main/Dataset/Match.csv",
    "Player.csv": "https://raw.githubusercontent.com/jwavalosq/TennisAnalytics/main/Dataset/Player.csv",
    "Stats.csv": "https://raw.githubusercontent.com/jwavalosq/TennisAnalytics/main/Dataset/Stats.csv",
    "original_README.md": "https://raw.githubusercontent.com/jwavalosq/TennisAnalytics/main/README.md",
    "original_LICENSE": "https://raw.githubusercontent.com/jwavalosq/TennisAnalytics/main/LICENSE",
}


def fetch(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"skip (exists): {dest}")
        return
    print(f"fetch: {url}")
    urllib.request.urlretrieve(url, dest)


def main():
    for name, url in ORIGINAL.items():
        fetch(url, os.path.join(RAW, name))
    for year in range(2000, 2025):
        fetch(
            f"https://raw.githubusercontent.com/Aneeshers/tennis-sackmann-archive/main/atp/atp_matches_{year}.csv",
            os.path.join(RAW, "sackmann_atp", f"atp_matches_{year}.csv"),
        )
        fetch(
            f"https://raw.githubusercontent.com/Aneeshers/tennis-sackmann-archive/main/wta/wta_matches_{year}.csv",
            os.path.join(RAW, "sackmann_wta", f"wta_matches_{year}.csv"),
        )
    print("done")


if __name__ == "__main__":
    main()
