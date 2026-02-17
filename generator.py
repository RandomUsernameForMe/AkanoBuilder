import argparse
import csv
import os
import re
import shutil
import sys
from typing import Dict, Any

import gdrive_client
import utils

# Configuration
INPUT_DIR = "inputs"
OUTPUT_DIR = "output"
FILES = {
    "csv": "characters.csv",
    "cores": "cores.docx",
    "origins": "origins.docx",
    "circles": "circles.docx",
    "units": "units.docx",
    "specializations": "specializations.docx"
}

# GOOGLE DRIVE CONFIGURATION
# Fill in the IDs from your Google Docs/Sheets URLs.
# If None, the script will use local files.
GDOC_IDS = {
    "csv": None,            # e.g., "1BxiM-..."
    "cores": "GDOC_ID_REMOVED",
    "origins": "GDOC_ID_REMOVED",
    "circles": "GDOC_ID_REMOVED",
    "units": "GDOC_ID_REMOVED",
    "specializations": "GDOC_ID_REMOVED"
}

def build_team_registry(cores_lib: Dict[str, Any]) -> Dict[str, str]:
    """
    Builds a team registry by iterating through the ordered H1 headers
    from the cores library. A team is defined by an H1 containing "Tým",
    and all subsequent characters belong to it until a new team is declared.
    """
    team_registry = {}
    current_team_name = "Neznámý"
 
    # The keys in cores_lib are ordered because Python dicts preserve insertion order since 3.7
    # and the parser reads the file sequentially.
    for h1_key in cores_lib.keys():
        # The h1_key is the cleaned H1 heading from the source file.
        # Check if it's a team definition.
        if "tým" in h1_key.lower():
            # This is a team heading. Update the current team name.
            current_team_name = h1_key
            print(f" [Team Found] {current_team_name}")
        else:
            # This is a character heading.
            team_registry[h1_key] = current_team_name
    return team_registry

def build_role_registry(rows: list) -> Dict[str, Dict[str, str]]:
    """
    Builds a lookup dictionary from character rows.
    Structure: { "Category": { "Role": "CharacterName" } }
    Example: { "Infantry": { "Captain": "Kael" } }
    """
    registry = {}
    for row in rows:
        name = row['name']
        for col in ['unit_role', 'circle_role']:
            if ':' in row[col]:
                category, role = row[col].split(':', 1)
                category = category.strip()
                role = role.strip()
                
                if category not in registry:
                    registry[category] = {}
                registry[category][role] = name
    return registry

def inject_references(text: str, category: str, registry: Dict[str, Dict[str, str]]) -> str:
    """
    Replaces role names in text with 'Role (Name)' if the role exists in the registry for the given category.
    """
    if category not in registry:
        return text

    # Sort roles by length (descending) to match specific titles first (e.g. "Vice Captain" before "Captain")
    roles = sorted(registry[category].keys(), key=len, reverse=True)

    for role in roles:
        char_name = registry[category][role]
        # Regex: Match 'role' as a whole word, NOT followed by the character name (to avoid double naming)
        pattern = re.compile(rf'\b{re.escape(role)}\b(?!\s*\(?{re.escape(char_name)}\)?)')
        text = pattern.sub(f"{role} ({char_name})", text)
    
    return text

def generate_stats_report(output_dir: str, cores_lib: Dict, origins_lib: Dict, units_lib: Dict, circles_lib: Dict, specs_lib: Dict):
    report_path = os.path.join(output_dir, "stats.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"--- JÁDRA (CORES) [{len(cores_lib)}] ---\n")
        for key in sorted(cores_lib.keys()):
            f.write(f"- {key}\n")
        f.write("\n")

        f.write(f"--- PŮVODY (ORIGINS) [{len(origins_lib)}] ---\n")
        for key in sorted(origins_lib.keys()):
            f.write(f"- {key}\n")
        f.write("\n")

        f.write(f"--- SPECIALIZACE [{len(specs_lib)}] ---\n")
        for key in sorted(specs_lib.keys()):
            f.write(f"- {key}\n")
        f.write("\n")

        f.write(f"--- JEDNOTKY (UNITS) [{len(units_lib)}] ---\n")
        for unit, data in sorted(units_lib.items()):
            roles = [k for k in data.keys() if not k.startswith("__")]
            f.write(f"{unit} ({len(roles)} rolí):\n")
            for role in sorted(roles):
                f.write(f"  - {role}\n")
        f.write("\n")

        f.write(f"--- KRUHY (CIRCLES) [{len(circles_lib)}] ---\n")
        for circle, data in sorted(circles_lib.items()):
            roles = [k for k in data.keys() if not k.startswith("__")]
            f.write(f"{circle} ({len(roles)} rolí):\n")
            for role in sorted(roles):
                f.write(f"  - {role}\n")
        f.write("\n")
    print(f"Stats report generated: {report_path}")

def main():
    if not shutil.which("pandoc"):
        print("Warning: Pandoc is not installed or not in PATH. Processing DOCX files will fail.")

    parser = argparse.ArgumentParser(description="Akano Character Generator")
    parser.add_argument("--dry-run", action="store_true", help="Download and validate inputs without overwriting files or generating output.")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(INPUT_DIR, exist_ok=True)

    # 1. Sync inputs from Google Drive
    print("--- Syncing inputs from Google Drive ---")
    if args.dry_run:
        print("(DRY RUN MODE: Files will be checked but not overwritten)")

    gdrive_client.download_gdoc(GDOC_IDS["csv"], os.path.join(INPUT_DIR, FILES["csv"]), is_sheet=True, dry_run=args.dry_run)
    
    for key in ["cores", "origins", "circles", "units", "specializations"]:
        gdrive_client.download_gdoc(GDOC_IDS[key], os.path.join(INPUT_DIR, FILES[key]), is_sheet=False, dry_run=args.dry_run)
    print("----------------------------------------\n")

    if args.dry_run:
        print("Dry run completed. Exiting.")
        return

    # Parse Markdown Libraries
    cores_lib = utils.parse_markdown(os.path.join(INPUT_DIR, FILES["cores"]))
    origins_lib = utils.parse_markdown(os.path.join(INPUT_DIR, FILES["origins"]))
    circles_lib = utils.parse_markdown(os.path.join(INPUT_DIR, FILES["circles"]))
    units_lib = utils.parse_markdown(os.path.join(INPUT_DIR, FILES["units"]))
    specs_lib = utils.parse_markdown(os.path.join(INPUT_DIR, FILES["specializations"]))

    # Process CSV
    csv_path = os.path.join(INPUT_DIR, FILES["csv"])
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        if GDOC_IDS["csv"] is None:
            print(" [!] Hint: The 'csv' ID in GDOC_IDS is set to None. Please add the Google Sheet ID in generator.py.")
        return

    print(f"Processing characters from {FILES['csv']}...")
    
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        required_columns = {'name', 'origin_id', 'specialization', 'gender', 'unit_role', 'circle_role'}
        if not reader.fieldnames or not required_columns.issubset(reader.fieldnames):
            missing = required_columns - set(reader.fieldnames if reader.fieldnames else [])
            print(f"Error: Missing required columns in CSV: {', '.join(missing)}")
            return

        rows = list(reader)

    # Build registry of who is what
    role_registry = build_role_registry(rows)
    team_registry = build_team_registry(cores_lib)

    # --- Validation Step: Check if all characters in CSV have a core entry ---
    print("\n--- Checking for missing core entries ---")
    missing_cores_found = False
    for row in rows:
        name = row['name']
        if name not in cores_lib:
            print(f" [!] Warning: Character '{name}' from CSV is missing a corresponding entry in {FILES['cores']}.")
            missing_cores_found = True
    if not missing_cores_found:
        print("All characters have a core entry. OK.")
    print("---------------------------------------\n")

    for row in rows:
        name = row['name']
        print(f"Processing {name}...", end=" ")
        
        # Extract keys and split H1:H2 where necessary
        unit_h1, unit_h2 = row['unit_role'].split(':', 1) if ':' in row['unit_role'] else (row['unit_role'], "")
        circle_h1, circle_h2 = row['circle_role'].split(':', 1) if ':' in row['circle_role'] else (row['circle_role'], "")

        # Get text and inject references
        unit_text = inject_references(utils.get_text(units_lib, row['unit_role']), unit_h1, role_registry)
        circle_text = inject_references(utils.get_text(circles_lib, row['circle_role']), circle_h1, role_registry)

        # Use full title from cores library if available (e.g. "Name (Title)")
        display_name = name
        if name in cores_lib and "__ORIGINAL_H1__" in cores_lib[name]:
            display_name = cores_lib[name]["__ORIGINAL_H1__"]

        team_name = team_registry.get(name, "Neznámý")

        content = f"# {display_name}\n"
        content += f"**Původ:** {row['origin_id']}\n"
        content += f"**Specializace:** {row['specialization']}\n"
        content += f"**Jednotka:** {unit_h1}\n"
        content += f"**Tým:** {team_name}\n"
        content += f"**Kruh:** {circle_h1}\n\n---\n\n"
        content += f"## Osobní historie\n{utils.get_text(cores_lib, row['name'])}\n\n"
        content += f"## Původ: {row['origin_id']}\n{utils.get_text(origins_lib, row['origin_id'])}\n\n"
        content += f"## Příslušnost k jednotce: {unit_h1}\n**Funkce:** {unit_h2}\n{unit_text}\n\n"
        content += f"## Zájmový kruh: {circle_h1}\n**Postavení:** {circle_h2}\n{circle_text}\n\n"
        content += f"## Specializace: {row['specialization']}\n{utils.get_text(specs_lib, row['specialization'])}\n"

        with open(os.path.join(OUTPUT_DIR, f"{utils.sanitize_filename(name)}.md"), 'w', encoding='utf-8') as out_f:
            out_f.write(content)
        print(f"Done -> {os.path.join(OUTPUT_DIR, utils.sanitize_filename(name))}.md")

    # Generate statistics report
    generate_stats_report(OUTPUT_DIR, cores_lib, origins_lib, units_lib, circles_lib, specs_lib)

if __name__ == "__main__":
    main()