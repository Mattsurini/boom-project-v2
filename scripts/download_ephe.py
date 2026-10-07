import os
import urllib.request
from pathlib import Path

EPHE_DIR = Path("E:/Boom Project/.ephe")
EPHE_DIR.mkdir(exist_ok=True)

# Swiss Ephemeris files from astro.com
BASE_URL = "https://www.astro.com/swisseph/ephe/"

FILES = [
    "seas_18.se1",   # Small planets 1800-2399
    "semo_18.se1",   # Moon 1800-2399
    "sepl_18.se1",   # Planets 1800-2399
    "sedeltat.txt",  # Delta T data
]

print(f"Downloading ephemeris files to {EPHE_DIR}...")

for fname in FILES:
    url = BASE_URL + fname
    dest = EPHE_DIR / fname
    
    if dest.exists():
        print(f"  {fname} already exists ({dest.stat().st_size} bytes)")
        continue
    
    try:
        print(f"  Downloading {fname}...")
        urllib.request.urlretrieve(url, str(dest))
        print(f"    OK ({dest.stat().st_size} bytes)")
    except Exception as e:
        print(f"    FAILED: {e}")

print(f"\nDone. Files in {EPHE_DIR}:")
for f in EPHE_DIR.iterdir():
    print(f"  {f.name} ({f.stat().st_size} bytes)")
