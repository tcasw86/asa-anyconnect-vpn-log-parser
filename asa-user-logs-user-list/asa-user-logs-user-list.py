import os
import re

# Folder containing the log files
log_folder = "./logs"  # Adjust as needed
output_folder = "./output"
os.makedirs(output_folder, exist_ok=True)

# Ensure the logs folder exists, or create it and alert the user
if not os.path.isdir(log_folder):
    os.makedirs(log_folder)
    print(f"🆕 Created missing logs folder at '{log_folder}'.")
    print("📂 Please add .txt log files into the 'logs' folder and re-run the script.")
    exit(1)  # Stop the script so user can add files

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

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

# Output to users.txt
with open(os.path.join(output_folder, "users.txt"), "w", encoding='utf-8') as output_file:
    for username in sorted(usernames):
        output_file.write(username + "\n")

print(f"✅ Extracted {len(usernames)} unique usernames to users.txt.")
