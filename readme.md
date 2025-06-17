# ASA AnyConnect VPN Log Parser
These scripts take input text log files and parse them

Both python scripts use a "logs" folder with text log files for input, run script once to create directory. Output will be located in the "output" directory. these folders sit in the directory above the scripts

## asa-user-logs-user-list
Takes a look at input logs for <username@domain.com> and puts it in a simple text list that is deduped

## asa-user-logs-csv
Takes input logs and puts them in a CSV file
