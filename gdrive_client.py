import os
import re
import requests

def validate_download(file_path: str, is_sheet: bool) -> bool:
    """
    Validates the format of the downloaded file.
    """
    try:
        # Read first few bytes to check signature
        with open(file_path, 'rb') as f:
            header = f.read(4)

        # Check for HTML (Google Login page)
        if b"<html" in header or b"<!DOC" in header:
             print(f"\n [!] Error: {os.path.basename(file_path)} appears to be a Google Login page. Check sharing permissions.")
             return False

        if is_sheet:
            # CSV Check
            if not content.strip():
                print(f"\n [!] Error: {os.path.basename(file_path)} is empty.")
                return False
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            if ',' not in content.splitlines()[0]:
                print(f"\n [!] Error: {os.path.basename(file_path)} does not look like a valid CSV (no commas in header).")
                return False
        else:
            # DOCX Check (Magic number for ZIP is PK\x03\x04)
            if header != b'PK\x03\x04':
                print(f"\n [!] Error: {os.path.basename(file_path)} is not a valid DOCX/ZIP file.")
                return False
        
        return True
    except Exception as e:
        print(f"\n [!] Validation error: {e}")
        return False

def download_gdoc(file_id: str, output_path: str, is_sheet: bool = False, dry_run: bool = False):
    """
    Downloads content from Google Docs/Sheets using export links.
    """
    if not file_id:
        return

    if is_sheet:
        # Export for Google Sheets -> CSV
        url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
    else:
        # Export for Google Docs -> TXT (Markdown)
        url = f"https://docs.google.com/document/d/{file_id}/export?format=docx"

    temp_path = output_path + ".tmp"
    print(f"Downloading {os.path.basename(output_path)} from Google Drive...", end=" ")
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        
        if validate_download(temp_path, is_sheet):
            if dry_run:
                print("Valid (Dry Run - Not overwriting)")
                os.remove(temp_path)
            else:
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(temp_path, output_path)
                print("Done")
        else:
            print("Skipped (Invalid format)")
            if os.path.exists(temp_path):
                os.remove(temp_path)
    except Exception as e:
        print(f"\n [!] Error downloading {output_path}: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)