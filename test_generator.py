import pytest
import generator

# --- Testy pro generator.py ---

def test_build_team_registry():
    """
    Testuje správné přiřazení postav k týmům na základě pořadí.
    """
    # Simulovaná data z `cores_lib` (slovník zachovává pořadí)
    mock_cores_lib = {
        "Úvodní postava": {},
        "Tým 1 - Kočky": {},
        "Mushashi": {},
        "Shigen": {},
        "Tým 2 - Princezna": {},
        "Kaya": {},
        "Poslední postava": {},
    }

    team_registry = generator.build_team_registry(mock_cores_lib)

    assert team_registry.get("Úvodní postava") == "Neznámý"
    assert team_registry.get("Mushashi") == "Tým 1 - Kočky"
    assert team_registry.get("Shigen") == "Tým 1 - Kočky"
    assert team_registry.get("Kaya") == "Tým 2 - Princezna"
    # Postava za posledním týmem by měla patřit k němu
    assert team_registry.get("Poslední postava") == "Tým 2 - Princezna"

def test_inject_references():
    """
    Testuje nahrazování rolí jmény postav.
    """
    mock_registry = {
        "Hvězdy": {
            "Kapitán": "Shiho",
            "Zástupce kapitána": "Anna"
        }
    }
    
    # Scénář 1: Jednoduché nahrazení
    text1 = "Náš Kapitán je skvělý."
    expected1 = "Náš Kapitán (Shiho) je skvělý."
    assert generator.inject_references(text1, "Hvězdy", mock_registry) == expected1

    # Scénář 2: Delší role se musí nahradit první
    text2 = "Zástupce kapitána je Anna, ale Kapitán je Shiho."
    expected2 = "Zástupce kapitána (Anna) je Anna, ale Kapitán (Shiho) je Shiho."
    assert generator.inject_references(text2, "Hvězdy", mock_registry) == expected2

    # Scénář 3: Nemělo by nahradit, pokud už jméno existuje
    text3 = "Role je Kapitán (Shiho)."
    expected3 = "Role je Kapitán (Shiho)."
    assert generator.inject_references(text3, "Hvězdy", mock_registry) == expected3

    # Scénář 4: Nemělo by nahradit podřetězec
    text4 = "Podkapitán není v registru."
    expected4 = "Podkapitán není v registru."
    assert generator.inject_references(text4, "Hvězdy", mock_registry) == expected4

    # Scénář 5: Kategorie neexistuje
    text5 = "Kapitán jiné jednotky."
    assert generator.inject_references(text5, "JINÁ JEDNOTKA", mock_registry) == text5