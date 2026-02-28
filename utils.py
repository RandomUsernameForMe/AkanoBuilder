import os
import re
import sys
import unicodedata
import shutil
import subprocess
from typing import Dict, Any

def sanitize_filename(value: str) -> str:
    """
    Sanitizes a string to be safe for filenames.
    Removes diacritics, replaces spaces with underscores, removes non-alphanumeric chars.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '_', value)

def parse_docx(file_path: str) -> str:
    """
    Extracts text from DOCX using Pandoc.
    """
    if not shutil.which("pandoc"):
        print(f" [!] Error: 'pandoc' is not installed or not in PATH. Cannot convert {os.path.basename(file_path)}.")
        return ""

    try:
        # Convert docx to markdown (gfm - GitHub Flavored Markdown)
        # --wrap=none prevents hard line wrapping which could break parsing
        cmd = ["pandoc", "-f", "docx", "-t", "gfm", "--wrap=none", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f" [!] Pandoc error on {os.path.basename(file_path)}: {result.stderr}")
            return ""
        
        # Save the intermediate Markdown file to disk for verification
        md_path = os.path.splitext(file_path)[0] + ".md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(result.stdout)

        return result.stdout
    except Exception as e:
        print(f" [!] Error running pandoc on {file_path}: {e}")
        return ""

def parse_markdown(file_path: str) -> Dict[str, Any]:
    """
    Parses a markdown file into a nested dictionary structure.
    Structure: { "H1": { "H2": "content", "__ROOT__": "content" } }
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)

    print(f"Parsing {os.path.basename(file_path)}...", end=" ")

    if file_path.endswith('.docx'):
        content = parse_docx(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

    # Remove HTML comments <!-- ... -->
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    # Normalize separators (---, \-\-\-, **---**, <span...>---</span> etc) to standard '---'
    content = re.sub(r'^[ \t]*(?:<[^>]+>)*[ \t]*(?:[\\*_]+[ \t]*)?(?:\\?-[ \t]*){3,}(?:[\\*_]+[ \t]*)?(?:<[^>]+>)*[ \t]*$', '---', content, flags=re.MULTILINE)

    # Remove custom comments bounded by '---' lines
    content = re.sub(r'^---\s*$.*?^---\s*$', '', content, flags=re.DOTALL | re.MULTILINE)

    lines = content.splitlines(keepends=True)

    data = {}
    current_h1 = None
    current_h2 = None
    buffer = []

    def flush_buffer():
        nonlocal buffer, current_h1, current_h2
        if not buffer:
            return
        
        text = "".join(buffer).strip()
        if not text:
            buffer = []
            return

        if current_h1 and not current_h2:
            if "__ROOT__" not in data[current_h1]:
                data[current_h1]["__ROOT__"] = ""
            data[current_h1]["__ROOT__"] += text
        elif current_h1 and current_h2:
            data[current_h1][current_h2] = text
        
        buffer = []

    for line in lines:
        # Check for H1
        if line.startswith("# "):
            flush_buffer()
            raw_h1 = line.lstrip("# ").rstrip()
            # Normalize H1: remove text in parentheses and prefixes like C001, S001
            current_h1 = re.sub(r'\s*\(.*?\)', '', raw_h1)
            current_h1 = re.sub(r'^[CS]\d+\s+', '', current_h1).strip()
            current_h1 = re.sub(r'[*_]+', '', current_h1).strip()
            
            current_h2 = None
            if current_h1 not in data:
                data[current_h1] = {}
            if raw_h1 != current_h1:
                data[current_h1]["__ORIGINAL_H1__"] = raw_h1
        # Check for H2
        elif line.startswith("## "):
            flush_buffer()
            raw_h2 = line.lstrip("# ").rstrip()
            current_h2 = re.sub(r'\s*\(.*?\)', '', raw_h2)
            current_h2 = re.sub(r'^[CS]\d+\s+', '', current_h2).strip()
        # Content (including H3+)
        else:
            buffer.append(line)
    
    flush_buffer()
    
    # Count stats for logging
    h1_count = len(data)
    h2_count = sum(len(v) for v in data.values())
    print(f"Done (found {h1_count} categories, {h2_count} sub-sections)")
    
    return data

def get_text(library: Dict[str, Any], key_string: str) -> str:
    """
    Retrieves text from library based on key string (H1 or H1:H2).
    """
    parts = key_string.split(':')
    h1 = parts[0].strip()
    
    if h1 not in library:
        print(f" [!] Missing Category: '{h1}'")
        return f"[MISSING: {key_string}]"

    if len(parts) > 1:
        h2 = parts[1].strip()
        if h2 not in library[h1]:
            print(f" [!] Missing Entry: '{h2}' in category '{h1}'. Using default text.")
            return library[h1].get("__ROOT__", f"[MISSING: {key_string}]")
        return library[h1][h2]
    else:
        if "__ROOT__" not in library[h1]:
            print(f" [!] Missing Root Content: '{h1}'")
            return f"[MISSING: {key_string}]"
        return library[h1]["__ROOT__"]