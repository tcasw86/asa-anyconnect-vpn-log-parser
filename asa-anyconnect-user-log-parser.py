import os
import re
import csv
from collections import defaultdict
from datetime import datetime

log_folder = "../logs"
output_folder = "../output"
output_txt = os.path.join(output_folder, "asa_user_list.txt")
output_csv = os.path.join(output_folder, "asa_log_report.csv")

# Ensure the logs folder exists, or create it and alert the user
if not os.path.isdir(log_folder):
    os.makedirs(log_folder)
    print(f"🆕 Created missing logs folder at '{log_folder}'.")
    print("📂 Please add .txt log files into the 'logs' folder and re-run the script.")
    exit(1)  # Stop the script so user can add files

# Ensure output directory exists
os.makedirs(output_folder, exist_ok=True)

min_date = None
max_date = None

# === 1️⃣ USERNAME LIST EXTRACTION ===

print("▶ Starting username extraction...")

# Extract month and day from the log line (first 2 tokens)
parts = line.split()
if len(parts) >= 3:
    try:
        # Convert e.g. "Jun 16" to a datetime object
        log_date = datetime.strptime(f"{parts[0]} {parts[1]}", "%b %d")
        
        # Update min and max dates
        if not min_date or log_date < min_date:
            min_date = log_date
        if not max_date or log_date > max_date:
            max_date = log_date
    except ValueError:
        pass  # skip

# Regex to capture email inside "User <email>"
email_pattern = re.compile(r'User <([^>]+)>')

# Set to store unique email usernames
usernames = set()

# Process each .txt file
for filename in os.listdir(log_folder):
    if filename.endswith(".txt"):
        filepath = os.path.join(log_folder, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                match = email_pattern.search(line)
                if match:
                    usernames.add(match.group(1))  # Extract email only

# Output to output_txt
with open(output_txt, "w", encoding='utf-8') as output_file:
    for username in sorted(usernames):
        output_file.write(username + "\n")

print(f"✅ Extracted {len(usernames)} unique usernames to {output_txt}")

# === 2️⃣ DETAILED CSV PARSING ===

print("▶ Starting detailed CSV parsing...")

# Mapping ASA attributes to human-readable column headers
FIELD_MAP = {
    "timestamp": "Timestamp",
    "User Name": "User Name",
    "IP Address": "IP Address",
    "aaa.cisco.grouppolicy": "Group Policy",
    "endpoint.anyconnect.devicetype": "Device Type",
    "endpoint.anyconnect.publicmacaddress": "MAC Address",
    "endpoint.anyconnect.devicecomputername": "Device Name",
}

# Regex to parse log lines
log_pattern = re.compile(
    r'^(?P<month>\w{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}):\d{2} .*?DAP: User (?P<user>[^,]+), Addr (?P<ip>[^:]+): '
    r'Session Attribute (?P<attribute>[^\s=]+) = ?(?P<value>.*)$'
)

# Grouped by (user, ip, timestamp string)
sessions = defaultdict(dict)

# Process all log files
for filename in os.listdir(log_folder):
    if filename.endswith(".txt"):
        with open(os.path.join(log_folder, filename), 'r', encoding='utf-8') as file:
            for line in file:
                match = log_pattern.match(line.strip())
                if match:
                    data = match.groupdict()
                    timestamp = f"{data['month']} {data['day']} {data['time']}"
                    session_key = (data["user"], data["ip"], timestamp)
                    session = sessions[session_key]

                    session["User Name"] = data["user"]
                    session["IP Address"] = data["ip"]
                    session["Timestamp"] = timestamp

                    attr = data["attribute"]
                    if attr in FIELD_MAP:
                        session[FIELD_MAP[attr]] = data["value"].strip('"')

# Write output CSV
with open(output_csv, "w", newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=FIELD_MAP.values())
    writer.writeheader()
    for session in sessions.values():
        writer.writerow({field: session.get(field, "") for field in FIELD_MAP.values()})

print(f"✅ Done. Wrote {len(sessions)} grouped login events to {output_csv}")

print("\n All processing complete!")