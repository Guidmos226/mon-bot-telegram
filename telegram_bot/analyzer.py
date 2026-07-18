"""
Analyse des messages du canal baccaratstat.

Format des messages :
  ⏰#N1019. 0(2♥️2♣️6♥️) - ▶ 0(A♦️9♥️)

  - #N1019  → numéro de jeu
  - 0(2♥️2♣️6♥️) → score(cartes JOUEUR)  ← on regarde ici
  - ▶ 0(A♦️9♥️)  → score(cartes banquier) ← ignoré

Logique par paire (impair + pair) :
  - Jeux N1019 + N1020 = signal #1
  - Jeux N1021 + N1022 = signal #2 ...
  - Si le JOUEUR a ♠ dans AU MOINS UN des deux jeux → signal "avec pique"
  - Si le JOUEUR n'a PAS ♠ dans les DEUX jeux      → signal "sans pique"

Alerte : dès que ♠ apparaît après au moins 1 signal sans pique.
"""
import re

SPADE = "♠"
CARD_SYMBOLS = "♠♣♦♥"

# Numéro de jeu : #N1019 ou #n1019
_GAME_NUM_RE = re.compile(r"#[Nn](\d+)")

# Cartes du joueur : premier groupe (...) après le numéro de jeu
# Format : "#N1019. <score>(<cartes joueur>) - ▶ <score>(<cartes banquier>)"
_PLAYER_CARDS_RE = re.compile(r"#[Nn]\d+[^(]*\(([^)]+)\)")


def parse_game_message(text: str) -> tuple[int, list[str]] | None:
    """
    Extrait (numéro_jeu, cartes_joueur) depuis un message du canal.
    Retourne None si le message ne correspond pas au format attendu.
    """
    num_match = _GAME_NUM_RE.search(text)
    if not num_match:
        return None

    game_number = int(num_match.group(1))

    cards_match = _PLAYER_CARDS_RE.search(text)
    if not cards_match:
        return None

    raw_cards = cards_match.group(1)
    # Filtre les symboles de cartes (ignore chiffres, lettres, emoji variante ️)
    cards = [ch for ch in raw_cards if ch in CARD_SYMBOLS]

    return game_number, cards


def player_has_spade(cards: list[str]) -> bool:
    """Vrai si le joueur a ♠ dans ses cartes."""
    return SPADE in cards


def is_odd_game(game_number: int) -> bool:
    """Jeu impair → début d'un nouveau signal."""
    return game_number % 2 == 1


def cards_to_str(cards: list[str]) -> str:
    return "".join(cards) if cards else "—"
