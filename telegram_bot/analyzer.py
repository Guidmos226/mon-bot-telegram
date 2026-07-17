"""
Analyse des messages de signaux.

Format des messages du canal :
  - Message de PRÉDICTION (à ignorer) :
      ┌#n905 #m4 #_S
      ├          3      _    5   ...
      ├♠ 99.9% ...
      ├♣ 99.9% ...
      ├♦ 99.9% ...
      ├♥ 33.3% ...
      (pas de ligne └ en bas)

  - Message de RÉSULTAT (à traiter) :
      ┌#n899 #m58
      ├          3      _    5   ...
      ├♠ 66.6% ...
      ...
      └♠♣♥          ← ligne résultat : cartes réellement sorties

Le bot extrait uniquement les cartes de la ligne └ et ignore
les symboles de cartes dans les lignes ├ (statistiques/prédictions).
"""
import re

CARD_SYMBOLS: frozenset[str] = frozenset("♠♣♦♥")
SPADE = "♠"

# Ligne de résultat : commence par └ suivi de symboles de cartes
_RESULT_LINE_RE = re.compile(r"^└([♠♣♦♥]+)", re.MULTILINE)


def is_result_message(text: str) -> bool:
    """
    Vrai si le message contient une ligne de résultat (└♠♣♦♥…).
    Ces messages indiquent les cartes réellement sorties à la fin du jeu.
    """
    return bool(_RESULT_LINE_RE.search(text))


def extract_result_cards(text: str) -> list[str]:
    """
    Extrait les cartes de la ligne résultat (└…).
    Retourne une liste ordonnée des symboles présents.
    Retourne [] si aucune ligne résultat trouvée.
    """
    match = _RESULT_LINE_RE.search(text)
    if not match:
        return []
    return [ch for ch in match.group(1) if ch in CARD_SYMBOLS]


def extract_game_number(text: str) -> str | None:
    """Extrait le numéro de jeu depuis la ligne d'en-tête (ex: #n905)."""
    match = re.search(r"#n(\d+)", text)
    return match.group(1) if match else None


def has_spade(cards: list[str]) -> bool:
    """Vérifie si ♠ est présent dans la liste des cartes du résultat."""
    return SPADE in cards


def cards_to_str(cards: list[str]) -> str:
    """Convertit la liste de cartes en chaîne lisible."""
    return "".join(cards) if cards else "aucune"
