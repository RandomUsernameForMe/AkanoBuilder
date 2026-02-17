import pytest
import utils

# --- Testy pro utils.py ---

@pytest.mark.parametrize("input_string, expected_output", [
    ("Příliš žluťoučký kůň", "prilis_zlutoucky_kun"),
    ("Tým 1 - Kočky", "tym_1_kocky"),
    ("  leading and trailing spaces  ", "leading_and_trailing_spaces"),
    ("Special/Chars!@#$%^&*", "specialchars"),
    ("C001 Mushashi (“drsňák”)", "c001_mushashi_drsnak"),
])
def test_sanitize_filename(input_string, expected_output):
    """Testuje, zda sanitizace názvů souborů funguje správně."""
    assert utils.sanitize_filename(input_string) == expected_output

def test_parse_markdown_structure(tmp_path):
    """Testuje základní parsování H1 a H2 nadpisů."""
    md_content = """
# Tým 1
Text pod týmem 1.

## Role 1
Text pod rolí 1.

# Postava A (drsňák)
Text o postavě A.

## Medailonek
Text medailonku.
"""
    p = tmp_path / "test.md"
    p.write_text(md_content, encoding='utf-8')

    data = utils.parse_markdown(str(p))

    # Ověření klíčů (očištěných nadpisů)
    assert "Tým 1" in data
    assert "Postava A" in data

    # Ověření struktury
    assert "Role 1" in data["Tým 1"]
    assert "Medailonek" in data["Postava A"]
    assert "__ROOT__" in data["Postava A"] # Text přímo pod H1

    # Ověření obsahu
    assert data["Tým 1"]["Role 1"] == "Text pod rolí 1."
    assert data["Postava A"]["__ROOT__"].strip() == "Text o postavě A."
    assert data["Postava A"]["Medailonek"] == "Text medailonku."
    
    # Ověření, že se závorky správně ořezávají
    assert "Postava A (drsňák)" not in data

def test_parse_markdown_removes_html_comments(tmp_path):
    """Testuje, že parsování markdownu správně odstraňuje HTML komentáře."""
    md_content = """
# Viditelný nadpis
Tento text by měl být vidět.

<!--
# Skrytý nadpis
Tento text by měl být ignorován.
-->

## Viditelný podnadpis
Tento text by měl být také vidět.
"""
    p = tmp_path / "test.md"
    p.write_text(md_content, encoding='utf-8')

    data = utils.parse_markdown(str(p))

    # Ověření, že viditelný obsah je přítomen
    assert "Viditelný nadpis" in data
    assert "Viditelný podnadpis" in data["Viditelný nadpis"]
    # Ověření, že komentovaný obsah chybí
    assert "Skrytý nadpis" not in data

def test_parse_markdown_removes_separator_comments(tmp_path):
    """Testuje, že parsování markdownu správně odstraňuje komentáře ohraničené '---'."""
    md_content = """
# Viditelný nadpis
Tento text je vidět.

---
# Skrytý nadpis v komentáři
Tento text by měl být ignorován.
---

## Viditelný podnadpis
Tento text je také vidět.
"""
    p = tmp_path / "test.md"
    p.write_text(md_content, encoding='utf-8')

    data = utils.parse_markdown(str(p))

    assert "Viditelný nadpis" in data
    assert "Viditelný podnadpis" in data["Viditelný nadpis"]
    assert "Skrytý nadpis v komentáři" not in data