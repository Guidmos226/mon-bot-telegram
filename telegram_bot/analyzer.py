"""
Analyse des messages de signaux.
Détecte et extrait les symboles de cartes (♠ ♣ ♦ ♥).
"""

# Symboles de cartes reconnus
CARD_SYMBOLS: frozenset[str] = frozenset("♠♣♦♥")
SPADE = "♠"


def extract_cards(text: str) -> list[str]:
    """Retourne la liste ordonnée des symboles de cartes trouvés dans `text`."""
    return [ch for ch in text if ch in CARD_SYMBOLS]


def is_signal_message(text: str) -> bool:
    """Vérifie si le message contient au moins un symbole de carte."""
    return any(ch in CARD_SYMBOLS for ch in text)


def has_spade(cards: list[str]) -> bool:
    """Vérifie si ♠ est présent dans la liste des cartes extraites."""
    return SPADE in cards


def cards_to_str(cards: list[str]) -> str:
    """Convertit la liste de cartes en chaîne lisible, ou 'aucune' si vide."""
    return "".join(cards) if cards else "aucune"
