import tinytuya
import json
import os
from datetime import datetime

ACCESS_ID = os.getenv("TUYA_ACCESS_ID")
ACCESS_KEY = os.getenv("TUYA_ACCESS_KEY")
REGION = os.getenv("TUYA_REGION", "us")
DEVICE_ID = os.getenv("TUYA_DEVICE_ID")

cloud = tinytuya.Cloud(apiRegion=REGION, apiKey=ACCESS_ID, apiSecret=ACCESS_KEY)

print("Fetching first page of logs...")

try:
    logs = cloud.getdevicelog(DEVICE_ID, size=50)
except Exception as e:
    print(f"API error: {e}")
    raise SystemExit(1)

if not logs.get("success"):
    print("Failed to fetch logs:", logs)
    raise SystemExit(1)

entries = logs.get("result", {}).get("logs", [])

filename = "latest.json"
if os.path.exists(filename):
    with open(filename, "r", encoding="utf-8") as f:
        try:
            existing = json.load(f)
        except json.JSONDecodeError:
            existing = []
else:
    existing = []

# Deduplicate by event_time (unique timestamp)
existing_times = {e.get("event_time") for e in existing if isinstance(e, dict)}
new_entries = [
    e for e in entries
    if e.get("event_time") not in existing_times
]

# Prepend new entries (newest first)
merged = new_entries + existing

print(f"Fetched {len(new_entries)} new logs, total {len(merged)}.")

# Save merged data
with open(filename, "w", encoding="utf-8") as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)

print(f"Updated {filename} at {datetime.now().isoformat()}")
