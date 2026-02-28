# AkanoBuilder – Uživatelská příručka

Generátor charakterových listů pro LARP. Ze zdrojových Google Docs a CSV tabulky sestaví Markdown profily pro každou postavu, které lze volitelně převést do PDF.

---

## Požadavky

### Python a balíčky
- Python 3.10+
- Nainstaluj balíčky: `pip install requests markdown jinja2 weasyprint`

### Pandoc (povinný)
Musí být nainstalován a v PATH systému.
- Stáhnout: https://pandoc.org/installing.html
- Ověření: `pandoc --version`

### GTK3 runtime (jen Windows, jen pro PDF)
Vyžaduje WeasyPrint pro generování PDF.
- Stáhnout: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

---

## Rychlý start

```bash
# 1. Vygeneruj charakterové listy
python generator.py

# 2. (Volitelně) Převeď na PDF
python md_to_pdf.py

# 3. Resetuj projekt (před novým spuštěním)
python cleanup.py

# 4. Spusť testy
pytest
```

---

## Konfigurace

### Google Drive IDs (`generator.py`, `GDOC_IDS`)

Na začátku souboru `generator.py` nastav ID jednotlivých Google dokumentů:

```python
GDOC_IDS = {
    "csv": None,              # None = použij lokální soubor; nebo ID Google Sheetu
    "cores": "...",           # ID dokumentu s jádry postav
    "origins": "...",         # ID dokumentu s původy
    "circles": "...",         # ID dokumentu s kruhy
    "units": "...",           # ID dokumentu s jednotkami
    "specializations": "...", # ID dokumentu se specializacemi
}
```

**Jak najít ID dokumentu:**
1. Otevři dokument v prohlížeči
2. Z URL zkopíruj část mezi `/d/` a `/edit`:
   - `https://docs.google.com/document/d/`**`1ssrrTV2Atyt1-...`**`/edit`

> Dokumenty musí být sdíleny jako „Kdokoliv s odkazem může zobrazit".

Pokud `csv` je `None`, je nutné mít soubor `inputs/characters.csv` lokálně.

---

## Struktura projektu

```
AkanoBuilder/
├── generator.py          # Hlavní skript: stažení + generování
├── gdrive_client.py      # Stahování z Google Drive
├── utils.py              # Parsování a pomocné funkce
├── md_to_pdf.py          # Převod MD → PDF
├── cleanup.py            # Čištění výstupů
├── convert_html_to_md.py # Konverze HTML exportů (legacy)
│
├── inputs/               # Zdrojová data
│   ├── characters.csv    # Tabulka postav (UTF-8, čárkami)
│   ├── cores.docx        # Jádra postav (staženo z Google Docs)
│   ├── origins.docx      # Původy
│   ├── units.docx        # Jednotky
│   ├── circles.docx      # Kruhy
│   └── specializations.docx
│
├── output/               # Vygenerované soubory
│   ├── *.md              # Jeden soubor na postavu
│   ├── stats.txt         # Přehledová statistika
│   └── pdf/              # Vygenerovaná PDF
│
└── templates/
    └── character.html    # Jinja2 šablona pro PDF
```

---

## Formát vstupních dat

### `inputs/characters.csv`

UTF-8, odděleno čárkami. Povinné sloupce:

| Sloupec | Příklad | Popis |
|--------|---------|-------|
| `name` | `Mushashi` | Jméno postavy; musí odpovídat H1 nadpisu v `cores.docx` |
| `origin_id` | `Místní` | Klíč původu (H1 nadpis v `origins.docx`) |
| `specialization` | `Shōka` | Klíč specializace |
| `gender` | `Muž` | Pohlaví (jen zobrazení) |
| `unit_role` | `Hagakure:Člen` | Jednotka a funkce ve formátu `H1:H2`; nebo jen `H1` |
| `circle_role` | `JPop:Člen` | Kruh a funkce; nebo jen `H1` |

### Struktura Google Dokumentů

Každý dokument musí dodržovat hierarchii nadpisů:

```
# Kategorie (H1)            ← klíč pro vyhledávání
Text přímo pod H1...        ← uložen jako __ROOT__

## Podkategorie (H2)        ← podklíč
Obsah sekce...

## Další podkategorie
Obsah...
```

**Normalizace H1 klíčů:**
- Kódy jako `C001`, `S001` jsou z klíče odebrány: `# C001 Mushashi` → klíč `Mushashi`
- Text v závorkách je odebrán: `# Mushashi ("drsňák")` → klíč `Mushashi`
- Originální H1 se ukládá pro zobrazení

**Skrývání obsahu:**
- HTML komentáře (`<!-- text -->`) jsou z výstupu odstraněny
- Sekce ohraničené `---` řádky jsou odstraněny (GM poznámky, spoilery):
  ```
  ---
  Toto se do výstupu nedostane.
  ---
  ```

---

## Průběh generování

1. **Stažení** — `gdrive_client.py` stáhne `.docx` a `.csv` z Google Drive
2. **Parsování** — pandoc převede `.docx` na `.md`; `utils.py` parsuje do slovníků
3. **Čtení CSV** — načtou se data postav, sestaví se registry týmů a rolí
4. **Generování** — pro každou postavu se zkombinují texty ze všech knihoven
5. **Reference** — do textu rolí se doplní jména postav (`Člen` → `Člen (Mushashi)`)
6. **Výstup** — soubory `output/*.md` + `output/stats.txt`

---

## Přehled příkazů

### `python generator.py`
Hlavní příkaz. Stáhne zdroje a vygeneruje charakterové listy.

```bash
python generator.py            # standardní spuštění
python generator.py --dry-run  # jen validace, nic nepřepíše
```

### `python md_to_pdf.py`
Převede soubory z `output/*.md` na PDF do `output/pdf/`.
Musí se spustit až po `generator.py`.

### `python cleanup.py`
Smaže celý adresář `output/` a soubory v `inputs/` kromě `characters.csv`.
Použij před novým spuštěním generátoru.

### `pytest`
Spustí testy pro parsování a generování.

```bash
pytest                # všechny testy
pytest test_utils.py  # jen testy pro utils.py
```

---

## Časté chyby

| Chyba | Příčina | Řešení |
|-------|---------|--------|
| `pandoc is not installed or not in PATH` | pandoc není v systému | Nainstaluj pandoc; ověř `pandoc --version` |
| `appears to be a Google Login page` | dokument není veřejně sdílen | Sdílej dokument → Kdokoliv s odkazem |
| `does not look like a valid CSV` | špatné ID nebo typ souboru | Ověř ID a sdílení Google Sheetu |
| `Missing required columns in CSV` | chybí povinný sloupec | Zkontroluj hlavičku CSV |
| `'characters.csv' not found` | chybí lokální CSV a ID je `None` | Přidej CSV do `inputs/` nebo nastav ID v `GDOC_IDS` |
| `Warning: Character missing core entry` | jméno v CSV nenalezeno v `cores.docx` | Přidej H1 nadpis `# Jméno` do cores dokumentu |
| `[MISSING: klíč]` ve výstupu | hodnota z CSV nenalezena v knihovně | Zkontroluj, že H1 v `.docx` odpovídá hodnotě v CSV |
| `WeasyPrint cannot find GTK` | chybí GTK3 runtime (Windows) | Nainstaluj GTK3 runtime; restartuj skript |
| `ModuleNotFoundError` | chybí Python balíček | `pip install requests markdown jinja2 weasyprint` |
