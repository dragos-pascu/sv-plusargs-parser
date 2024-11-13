# sv-plusargs-parser

# Plusarg Scanner for Verilog/SystemVerilog Files

This script scans Verilog and SystemVerilog files for `$test$plusargs` and `$value$plusargs` patterns, retrieves metadata such as author, file location, and line number, and provides tools to manage and document these "plusargs."

## Features

- **Scan for Plusargs**: Automatically locate and document plusargs from Verilog/SystemVerilog files.
- **Author Information**: Retrieve and display authors using SVN blame for each plusarg.
- **Description Editing**: Edit and update plusarg descriptions interactively.
- **Export to CSV**: Export plusarg data to a CSV file for easy reference.
- **JSON Logging**: Track changes to plusargs over time in a JSON log file.
- **Search and Filter**: Search for plusargs based on keywords.
- **List Authors**: Summarize the number of plusargs by each author.

## Requirements

- **Python** (version 3.6+)
- **SVN**: Subversion must be installed and configured for the `blame` feature.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/plusarg-scanner.git
   cd plusarg-scanner

2. Usage
  python plusarg_scanner.py <directory> [options]
<directory>: The root directory to scan for Verilog/SystemVerilog files.
Options
--list: Lists all plusargs, allowing interactive description updates.
--export: Exports plusarg data to a CSV file in the specified directory.
--log: Enables JSON logging of plusargs and changes.
--search <keyword>: Searches for plusargs by keyword in name or description.
--list-authors: Lists authors and the count of plusargs associated with each.
Examples


Scan Directory and Log Results

  ```bash
python plusarg_scanner.py ./verilog_project --log
#Export Plusargs to JSON

python plusarg_scanner.py ./verilog_project --list
#Show the list of plusargs from JSON file

python plusarg_scanner.py ./verilog_project --search "reset"
#Search plusarg by name

python plusarg_scanner.py ./verilog_project --list-authors
#List Authors and Plusarg Counts

