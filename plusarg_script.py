import os
import re
import argparse
import csv
import json
import subprocess
from datetime import datetime

def get_author_of_plusarg(file_path, line_number):
    try:
        result = subprocess.run(
            ['svn', 'blame', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        output = result.stdout.decode().splitlines()
        for i, line in enumerate(output):
            if i + 1 == line_number:
                parts = line.split()
                if len(parts) > 1:
                    author = parts[1]
                    return author
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving SVN info for {file_path}: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return "Unknown"

def scan_files(directory, log=False):
    plusargs = {}
    plusarg_test_pattern = re.compile(r'\$test\$plusargs\("([^"]+)"\)')
    plusarg_value_pattern = re.compile(r'\$value\$plusargs\("([^"]+?)=')
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.v') or file.endswith('.sv') or file.endswith('.svh'):
                file_path = os.path.join(root, file)
                if log:
                    print(f"Scanning file: {file_path}")
                try:
                    with open(file_path, 'r') as f:
                        for line_number, line in enumerate(f, start=1):
                            matches_test = plusarg_test_pattern.findall(line)
                            matches_value = plusarg_value_pattern.findall(line)
                            all_matches = set(matches_test + matches_value)
                            for match in all_matches:
                                if match not in plusargs:
                                    author = get_author_of_plusarg(file_path, line_number)
                                    plusargs[match] = {
                                        "description": f"Description for {match}",
                                        "file": file_path,
                                        "line": line_number,
                                        "author": author
                                    }
                except IOError as e:
                    print(f"Error reading file {file_path}: {e}")
    return plusargs

def list_authors(plusargs):
    """
    Lists authors and the number of plusargs associated with each.
    """
    author_count = {}
    for info in plusargs.values():
        author = info['author']
        if author in author_count:
            author_count[author] += 1
        else:
            author_count[author] = 1
    print("Authors and their plusargs count:")
    for author, count in author_count.items():
        print(f"{author}: {count} plusargs")

def list_and_select_plusargs(plusargs, log_file_path):
    while True:
        print("Available plusargs:")
        for i, (plusarg, info) in enumerate(plusargs.items(), start=1):
            print(f"{i}. {plusarg}: {info['description']}")
        author_name = input("Enter the author's name to filter plusargs (or 'exit' to quit): ").strip()
        if author_name.lower() == 'exit':
            break
        filtered_plusargs = {
            k: v for k, v in plusargs.items() if v['author'].lower() == author_name.lower()
        }
        if filtered_plusargs:
            print(f"Plusargs by author {author_name}:")
            for i, (plusarg, info) in enumerate(filtered_plusargs.items(), start=1):
                status = "updated" if info['description'] != f"Description for {plusarg}" else "missing"
                print(f"{i}. {plusarg}: {status} - Current Description: {info['description']}")
            while True:
                try:
                    selection = input("Enter the number of the plusarg to update its description (or 'back' to choose a different author): ").strip()
                    if selection.lower() == 'back':
                        break
                    index = int(selection) - 1
                    if 0 <= index < len(filtered_plusargs):
                        selected_plusarg = list(filtered_plusargs.keys())[index]
                        new_description = input(f"Enter new description for '{selected_plusarg}': ").strip()
                        plusargs[selected_plusarg]['description'] = new_description
                        print(f"Description for '{selected_plusarg}' updated to: {new_description}")
                        save_plusargs(plusargs, log_file_path)  # Save changes to the JSON file
                    else:
                        print("Invalid selection. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a valid number or 'back'.")
        else:
            print(f"No plusargs found for author {author_name}.")
    return plusargs

def export_plusargs_to_csv(plusargs, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Plusarg', 'Description', 'File', 'Line', 'Author']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for plusarg, info in plusargs.items():
            writer.writerow({
                'Plusarg': plusarg,
                'Description': info['description'],
                'File': info['file'],
                'Line': info['line'],
                'Author': info['author']
            })

def update_json_log(plusargs, log_file):
    timestamp = datetime.now().isoformat()
    log_entry = {'timestamp': timestamp, 'plusargs': plusargs}
    log_data = [log_entry]
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=4)

def save_plusargs(plusargs, file_path):
    with open(file_path, 'w') as f:
        json.dump(plusargs, f, indent=4)

def load_plusargs(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                plusargs = json.load(f)
                if isinstance(plusargs, dict):
                    return plusargs  # Return the plusargs dictionary directly
                else:
                    print("Invalid JSON structure.")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
    return {}

def search_plusargs(plusargs, keyword):
    filtered = {k: v for k, v in plusargs.items() 
                if keyword.lower() in k.lower() or keyword.lower() in v['description'].lower()}
    return filtered

def main():
    parser = argparse.ArgumentParser(description="Scan plusargs in Verilog/SystemVerilog files.")
    parser.add_argument("directory", help="The directory to scan for plusargs.")
    parser.add_argument('--list', action='store_true', help='List all plusargs and allow selection to change description')
    parser.add_argument('--export', action='store_true', help='Export plusargs to a CSV file')
    parser.add_argument('--log', action='store_true', help='Log changes to plusargs over time')
    parser.add_argument('--search', help='Search and filter plusargs based on a keyword')
    parser.add_argument('--list-authors', action='store_true', help='List authors and the number of plusargs associated with each')
    args = parser.parse_args()

    log_file_path = os.path.join(args.directory, "plusargs_log.json")

    if args.log:
        plusargs = scan_files(args.directory, log=args.log)
        save_plusargs(plusargs, log_file_path)
    else:
        plusargs = load_plusargs(log_file_path)

    print("Plusargs loaded:", plusargs)  # Debugging output

    if args.list:
        plusargs = list_and_select_plusargs(plusargs, log_file_path)

    if args.export:
        export_csv_path = os.path.join(args.directory, "plusargs_inventory.csv")
        export_plusargs_to_csv(plusargs, export_csv_path)
        print(f"Plusargs inventory has been exported to {export_csv_path}")

    if args.search:
        filtered_plusargs = search_plusargs(plusargs, args.search)
        if filtered_plusargs:
            print("Filtered plusargs:")
            for plusarg, info in filtered_plusargs.items():
                print(f"Plusarg: {plusarg}")
                print(f" Description: {info['description']}")
                print(f" File: {info['file']}")
                print(f" Line: {info['line']}")
                print(f" Author: {info['author']}")
                print()
        else:
            print("No plusargs found with the specified keyword.")

    if args.list_authors:
        list_authors(plusargs)

if __name__ == "__main__":
    main()
