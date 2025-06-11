import os
import re
import csv
from collections import defaultdict

log_folder = "./logs"
output_folder = "./output"
output_csv = os.path.join(output_folder, "asa_log_report.csv")

# Ensure output directory exists
os.makedirs(output_folder, exist_ok=True)

# Mapping ASA attributes to human-readable column headers
FIELD_MAP = {
    "aaa.cisco.username": "User Name",
    "Addr": "IP Address",
    "aaa.cisco.grouppolicy": "Group Policy",
    "timestamp": "Timestamp",
    "aaa.cisco.tunnelgroup": "Tunnel Group",
    "endpoint.anyconnect.platform": "Platform",
    "endpoint.anyconnect.macaddress[0]": "MAC Address",
    "endpoint.anyconnect.useragent": "AnyConnect Version",
    "endpoint.anyconnect.devicecomputername": "Device Name",
    "endpoint.anyconnect.deviceuniqueid": "Device ID",
    "endpoint.anyconnect.devicetype": "Device Type",
}

# Regex to parse log lines
log_pattern = re.compile(
    r'^(?P<timestamp>\d{2}:\d{2}):\d{2} .*?DAP: User (?P<user>[^,]+), Addr (?P<ip>[^:]+): '
    r'Session Attribute (?P<attribute>[^\s=]+) = ?(?P<value>.*)$'
)

# Grouped by (user, ip, hh:mm)
sessions = defaultdict(dict)

# Process all log files
for filename in os.listdir(log_folder):
    if filename.endswith(".txt"):
        with open(os.path.join(log_folder, filename), 'r', encoding='utf-8') as file:
            for line in file:
                match = log_pattern.match(line.strip())
                if match:
                    data = match.groupdict()
                    session_key = (data["user"], data["ip"], data["timestamp"])
                    session = sessions[session_key]

                    session["User Name"] = data["user"]
                    session["IP Address"] = data["ip"]
                    session["Timestamp"] = data["timestamp"]

                    attr = data["attribute"]
                    if attr in FIELD_MAP:
                        session[FIELD_MAP[attr]] = data["value"]

# Write output CSV
with open(output_csv, "w", newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=FIELD_MAP.values())
    writer.writeheader()
    for session in sessions.values():
        writer.writerow({field: session.get(field, "") for field in FIELD_MAP.values()})

print(f"✅ Done. Wrote {len(sessions)} grouped login events to {output_csv}")