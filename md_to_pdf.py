import os
import sys

# Pokus o automatické přidání GTK3 do PATH na Windows
if os.name == 'nt':
    gtk_paths = [
        r"C:\Program Files\GTK3-Runtime Win64\bin",
        r"C:\Program Files (x86)\GTK3-Runtime Win64\bin"
    ]
    for path in gtk_paths:
        if os.path.exists(path) and path not in os.environ['PATH']:
            os.environ['PATH'] = path + os.pathsep + os.environ['PATH']

try:
    import markdown
    from jinja2 import Environment, FileSystemLoader
    from weasyprint import HTML
except ImportError as e:
    print(f" [!] Chyba: Chybí Python knihovna: {e}")
    print("     Nainstaluj závislosti: pip install markdown jinja2 weasyprint")
    sys.exit(1)
except OSError as e:
    print(f" [!] Chyba: WeasyPrint nemůže načíst systémové knihovny (GTK).")
    print(f"     Detail: {e}")
    print("     Na Windows je nutné nainstalovat GTK3 runtime a přidat ho do PATH.")
    print("     Stáhnout zde: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases")
    sys.exit(1)

# Konfigurace
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
PDF_DIR = os.path.join(OUTPUT_DIR, "pdf")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
TEMPLATE_FILE = "character.html"

def main():
    # 1. Kontrola složek
    if not os.path.exists(OUTPUT_DIR):
        print(f"Složka {OUTPUT_DIR} neexistuje. Nejprve spusť generator.py.")
        return

    if not os.path.exists(PDF_DIR):
        try:
            os.makedirs(PDF_DIR)
            print(f"Vytvořena složka {PDF_DIR}.")
        except OSError as e:
            print(f"Chyba při vytváření složky {PDF_DIR}: {e}")
            return

    if not os.path.exists(TEMPLATE_DIR):
        try:
            os.makedirs(TEMPLATE_DIR)
            print(f"Vytvořena složka {TEMPLATE_DIR}.")
        except OSError as e:
            print(f"Chyba při vytváření složky {TEMPLATE_DIR}: {e}")
            return

    # Vytvoření výchozí šablony, pokud neexistuje
    template_path = os.path.join(TEMPLATE_DIR, TEMPLATE_FILE)
    if not os.path.exists(template_path):
        print(f"Vytvářím výchozí šablonu {TEMPLATE_FILE}...")
        default_html = """<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        body { font-family: sans-serif; line-height: 1.6; padding: 20px; }
        h1 { color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }
        h2 { color: #e67e22; margin-top: 20px; }
        p { margin-bottom: 10px; }
    </style>
</head>
<body>
    {{ content }}
</body>
</html>"""
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(default_html)

    # 2. Příprava Jinja2 prostředí (načítání šablon)
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    try:
        template = env.get_template(TEMPLATE_FILE)
    except Exception as e:
        print(f"Chyba: Nelze načíst šablonu '{TEMPLATE_FILE}' ze složky '{TEMPLATE_DIR}'.")
        print(f"Ujisti se, že soubor existuje.")
        return

    # 3. Zpracování souborů
    print(f"Hledám .md soubory v {OUTPUT_DIR}...")
    
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".md")]
    if not files:
        print("Žádné .md soubory nenalezeny.")
        return

    count = 0
    for filename in files:
        md_path = os.path.join(OUTPUT_DIR, filename)
        pdf_filename = filename.replace(".md", ".pdf")
        pdf_path = os.path.join(PDF_DIR, pdf_filename)
        
        print(f"Konvertuji {filename} -> {pdf_filename}...", end=" ")
        
        try:
            # Načtení MD obsahu
            with open(md_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Konverze MD -> HTML
            # 'extra' zapíná podporu pro tabulky, definice atd.
            html_content = markdown.markdown(text, extensions=['extra'])
            
            # Vykreslení do HTML šablony (dosazení obsahu)
            rendered_html = template.render(
                content=html_content,
                title=filename.replace(".md", "").replace("_", " ").title()
            )
            
            # Generování PDF
            # base_url je důležité, aby WeasyPrint našel CSS soubor ve složce templates
            HTML(string=rendered_html, base_url=TEMPLATE_DIR).write_pdf(pdf_path)
            
            print("Hotovo.")
            count += 1
            
        except Exception as e:
            print(f"Chyba: {e}")

    print(f"\nDokončeno. Vygenerováno {count} PDF souborů.")

if __name__ == "__main__":
    main()