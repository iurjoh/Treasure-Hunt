"""Treasure Hunt game engine (revival).

Pure state machine with no input()/print() inside: the terminal CLI
(run.py), the browser front-end (web/, via Pyodide) and the test suite
all drive this same engine, so behaviour is identical everywhere.

Revival fixes from the 2026-09-30 audit:
- P0: restart now replays the SAME match (same board size and treasure
  location) instead of silently starting a brand-new adventure.
- P0: EOF / invalid input are handled with clean messages, no tracebacks.
- P0: all output is plain str; run.py reconfigures stdout to UTF-8 so the
  quotes/art never crash on cp1252 terminals.
- P2: the unprotected while True wrappers became explicit states.

2026-10-29 (owner request): bilingual EN/PT-BR. The first state asks for
the language BEFORE the welcome/name prompt, so the greeting already
appears in the chosen language. All player-facing text lives in STRINGS;
the English pack is byte-identical to the pre-bilingual version. The
ASCII banner is language-neutral (the drawn title is the game's logo)
and the end-game quotes keep their authors' attribution in both packs.
"""

import random

BANNER = '******************************************************************\n                   |                 |                     |\n________________.="";=.______________|_____________________|_____\n         |  ,-"_,=""     `"=.|                  |\n_________|__"=._o`"-._        `"=.______________|________________\n                `"=._o`"=._      _`"=._                     |\n_____________________:=._o "=._."_.-="\'"=.__________________|____\n         |    __.--" , ; `"=._o." ,-"""-._ ".   |\n_________|_._"  ,. .` ` `` ,  `"-._"-._   ". \'__|________________\n           |o`"=._` , "` `; .". ,  "-._"-._; ;              |\n___________| ;`-.o`"=._; ." ` \'"`.\` . "-._ /_______________|____\n         | |o;    `"-.o`"=._``  \'"` " ,__.--o;  |\n_________|_| ;     (#) `-.o `"=.`_.--"_o.-; ;___|_________________\n/______/___|o;._    "      `".o|o_.--"    ;o;____/______/______/__\n___/______/_"=._o--._        ; | ;        ; ;/______/______/______\n/______/______/__"=._o--._   ;o|o;     _._;o;____/______/______/__\n___/______/______/____"=._o._; | ;_.--"o.--"_/______/______/______\n/______/______/______/______"=.o|o_.--""___/______/______/______/_\n___/______/______/______/______/______/______/______/______/______\n   ).-.o.*)    +-+-+-+-+-+-+-+-+ +-+-+-+-+ +-+-+-+-+    ).-.o.*)\n  (:_.:.*(     |T|r|e|a|s|u|r|e| |H|u|n|t| |G|a|m|e|   (:_.:.*(\n   )*.-.o.)                                             )*.-.o.)\n  (-X_.*:(             |b|y| |i|u|r|j|o|h|             (-X_.*:(\n   )-.--.*)    +-+-+-+ +-+-+ +-+-+-+-+-+-+ +-+-+-+-+    )-.--.*)                          \n'

WIN_ART = '                ______\n             .-\'      `-.\n           .\'            `.\n          /                \\.\n         ;                 ;`\n         |          /      |;\n         ;         / / /   ;|\n         \'\\       / / /   / ;\n          \\`.    / /    .\' /\n           `.`-._____.-\' .\'\n             / /`_____.-\'\n            / / /\n           / / /    \n          / / /    "History may be accurate.\n         / / /       \n        / / /       But archaeology is precise."\n       / / /         \n      / / /         ― Doug Scott\n     / / /\n    / / /\n    \\/_/                          \n'

LOSS_ART = '\n         ,---,_          ,\n          _>   `\'-.  .--\'/\n     .--\'` ._      `/   <_\n      >,-\' ._\'.. ..__ . \' \'-.       "Failure\n   .-\'   .\'`         `\'.     \'.\n    >   / >`-.     .-\'< \\ , \'._\\.    is success\n   /    ; \'-._>   <_.-\' ;  \'._>\n   `>  ,/  /___\\ /___\\  \\_  /        in progress."\n   `.-|(|  \\_o/  \\_o/   |)|`\n       \\;        \\      ;/           ― Albert Einstein\n         \\  .-,   )-.  /\n          /`  .\'-\'.  `\\.\n         ;_.-`.___.\'-.;\n'

# PT-BR variants of the end-game art: same drawings, translated quotes,
# authors' attribution kept. Quote lines chosen to stay within the
# original line widths so the layout is unchanged.
WIN_ART_PT = WIN_ART.replace(
    '"History may be accurate.', '"A história pode ser exata.'
).replace(
    'But archaeology is precise."', 'Mas a arqueologia é precisa."'
)

LOSS_ART_PT = LOSS_ART.replace('"Failure', '"O fracasso').replace(
    'is success', 'é o sucesso'
).replace('in progress."', 'em progresso."')

VALID_SIZES = (3, 5, 9)
LEVEL_SIZES = {"1": 3, "2": 5, "3": 9}

# First-screen language choice, shown BEFORE the welcome/name prompt.
# Language-neutral on purpose: numbers only, both languages named in
# their own tongue, so no prior language is needed to answer it.
LANG_MENU = (
    "Choose your language / Escolha seu idioma:\n"
    "1. English\n"
    "2. Português (Brasil)"
)
LANG_PROMPT = "Enter your choice / Digite sua escolha (1-2): "
LANG_INVALID = (
    "Invalid choice. Please, enter 1 or 2. / Escolha inválida. Digite 1 ou 2."
)
LANG_CHOICES = {"1": "en", "2": "pt"}

# Every player-facing string, per language. Templates use .format()
# placeholders: {name}, {size}, {guesses}, {guess}, {max}, {row}, {col}.
# The "en" pack is byte-identical to the pre-bilingual engine so the
# existing English experience is preserved exactly.
STRINGS = {
    "en": {
        "name_prompt": "Welcome explorer! Please, enter your name (only letters): ",
        "level_menu": (
            "Please, choose your difficulty level:\n"
            "1. Easy (board size: 3x3)\n"
            "2. Medium (board size: 5x5)\n"
            "3. Hard (board size: 9x9)"
        ),
        "level_prompt": "Enter your choice (1-3): ",
        "farewell": "Thanks for playing! Come back soon!",
        "invalid_name": (
            "Invalid name. Please, enter a non-empty name"
            " with only letters from A to Z."
        ),
        "invalid_level": "Invalid choice. Please, enter a number between 1 and 3.",
        "board_intro": "Board size: {size}x{size}. Treasure: 1. Guesses: {guesses}.",
        "round_prompt": (
            "Explorer {name}, where should we dig now?"
            " Guess {guess} of {guesses}."
        ),
        "choose_row": "Choose a row: ",
        "choose_col": "Choose a column: ",
        "invalid_coord": (
            "Invalid option, explorer {name}."
            " Please, enter valid numbers between 0 and {max}."
        ),
        "out_of_map": "Sorry explorer {name}, those coordinates are outside the map.",
        "already_explored": (
            "This location was explored. Please, try a new one explorer {name}."
        ),
        "win": "Congratulations explorer {name}! You found the treasure!",
        "miss": "Sorry, explorer {name}. You missed the treasure!",
        "lose": "Sorry, explorer {name}. You didn't find the treasure this time.",
        "reveal": "The treasure was hidden in location ({row}, {col}).",
        "menu": (
            "Explorer {name}, what now?\n"
            "R - Replay the same map (same treasure location)\n"
            "N - New adventure (choose the difficulty)\n"
            "Q - Quit"
        ),
        "menu_prompt": "Choose (R/N/Q): ",
        "menu_replay": "Same map, explorer. The treasure stayed where it was. Good luck!",
        "invalid_menu": "Invalid input. Please, enter R, N or Q.",
        "game_over": "The game is over. Reload to play again.",
        "eof_text": "Input closed. ",
        "interrupt_text": "Interrupted. ",
        "win_art": WIN_ART,
        "loss_art": LOSS_ART,
        "quit_keys": ("Q",),
        "quit_label": "Q",
    },
    "pt": {
        "name_prompt": "Boas-vindas, explorador(a)! Digite seu nome (apenas letras): ",
        "level_menu": (
            "Escolha o nível de dificuldade:\n"
            "1. Fácil (tabuleiro: 3x3)\n"
            "2. Médio (tabuleiro: 5x5)\n"
            "3. Difícil (tabuleiro: 9x9)"
        ),
        "level_prompt": "Digite sua escolha (1-3): ",
        "farewell": "Obrigado por jogar! Volte em breve!",
        "invalid_name": (
            "Nome inválido. Digite um nome não vazio, usando apenas letras."
        ),
        "invalid_level": "Escolha inválida. Digite um número entre 1 e 3.",
        "board_intro": "Tabuleiro: {size}x{size}. Tesouros: 1. Tentativas: {guesses}.",
        "round_prompt": "{name}, onde devemos cavar agora? Tentativa {guess} de {guesses}.",
        "choose_row": "Escolha uma linha: ",
        "choose_col": "Escolha uma coluna: ",
        "invalid_coord": "Opção inválida, {name}. Digite números válidos entre 0 e {max}.",
        "out_of_map": "Desculpe, {name}, essas coordenadas estão fora do mapa.",
        "already_explored": "Este local já foi explorado. Tente um novo, {name}.",
        "win": "Parabéns, {name}! Você encontrou o tesouro!",
        "miss": "Que pena, {name}. Você não acertou o tesouro!",
        "lose": "Fim de jogo, {name}. Você não encontrou o tesouro desta vez.",
        "reveal": "O tesouro estava escondido na posição ({row}, {col}).",
        "menu": (
            "{name}, e agora?\n"
            "R - Repetir o mesmo mapa (mesma posição do tesouro)\n"
            "N - Nova aventura (escolher a dificuldade)\n"
            "S - Sair"
        ),
        "menu_prompt": "Escolha (R/N/S): ",
        "menu_replay": "Mesmo mapa. O tesouro continua onde estava. Boa sorte!",
        "invalid_menu": "Entrada inválida. Digite R, N ou S.",
        "game_over": "O jogo acabou. Recarregue para jogar de novo.",
        "eof_text": "Entrada encerrada. ",
        "interrupt_text": "Interrompido. ",
        "win_art": WIN_ART_PT,
        "loss_art": LOSS_ART_PT,
        # Q also quits in PT-BR: players used to the English version or
        # to common gaming conventions may type it; S is the documented key.
        "quit_keys": ("S", "Q"),
        "quit_label": "S",
    },
}


def board_text(board):
    """Renders the 2D board exactly like the original CLI did."""
    size = len(board)
    lines = ["   " + " ".join(str(col) for col in range(size))]
    for row in range(size):
        lines.append(f"{row}  " + " ".join(board[row]))
    return "\n".join(lines)


class TreasureHunt:
    """One Treasure Hunt session. Drive it with start()/submit()/eof().

    lang: None (default) starts at the language-choice state; "en" or
    "pt" skips it and starts directly at the name prompt in that
    language (used by the CLI env hook, the ?lang= URL hook and tests).
    """

    STATES = ("lang", "name", "level", "row", "col", "menu", "done")

    def __init__(self, rng=None, lang=None):
        if lang is not None and lang not in STRINGS:
            raise ValueError(f"unsupported language: {lang!r}")
        self.rng = rng if rng is not None else random.Random()
        self.lang = lang
        self.S = STRINGS[lang] if lang is not None else None
        self.state = "name" if lang is not None else "lang"
        self.name = None
        self.size = None
        self.board = None
        self.chest_row = None
        self.chest_col = None
        self.max_guesses = 0
        self.guess_num = 0
        self._row = None

    def start(self):
        """First screen: banner plus the language menu or the name prompt."""
        if self.lang is None:
            return [("art", BANNER), ("text", LANG_MENU), ("prompt", LANG_PROMPT)]
        return [("art", BANNER), ("prompt", self.S["name_prompt"])]

    def eof(self):
        """Clean exit on Ctrl+D / closed stdin, from any state."""
        self.state = "done"
        # Before a language is chosen, fall back to English for this
        # edge message (the visible menu itself is bilingual).
        pack = self.S or STRINGS["en"]
        return [("text", pack["eof_text"] + pack["farewell"])]

    def interrupt(self):
        """Clean exit on Ctrl+C, from any state."""
        self.state = "done"
        pack = self.S or STRINGS["en"]
        return [("text", pack["interrupt_text"] + pack["farewell"])]

    def submit(self, text):
        """Feeds one line of player input, returns (kind, text) output pairs."""
        if self.state == "done":
            pack = self.S or STRINGS["en"]
            return [("error", pack["game_over"])]
        handler = getattr(self, "_in_" + self.state)
        return handler(text)

    # -- setup ------------------------------------------------------

    def _in_lang(self, text):
        lang = LANG_CHOICES.get(text.strip())
        if lang is None:
            return [("error", LANG_INVALID), ("prompt", LANG_PROMPT)]
        self.lang = lang
        self.S = STRINGS[lang]
        self.state = "name"
        return [("prompt", self.S["name_prompt"])]

    def _new_game(self, size, chest=None):
        self.size = size
        self.board = [["-"] * size for _ in range(size)]
        if chest is None:
            chest = (
                self.rng.randint(0, size - 1),
                self.rng.randint(0, size - 1),
            )
        self.chest_row, self.chest_col = chest
        self.max_guesses = int(size * 1.5)
        self.guess_num = 1
        self._row = None
        self.state = "row"
        intro = self.S["board_intro"].format(size=size, guesses=self.max_guesses)
        return [("text", intro)] + self._round_prompt()

    def _round_prompt(self):
        return [
            (
                "text",
                self.S["round_prompt"].format(
                    name=self.name, guess=self.guess_num, guesses=self.max_guesses
                ),
            ),
            ("board", board_text(self.board)),
            ("prompt", self.S["choose_row"]),
        ]

    def _menu(self):
        self.state = "menu"
        return [
            ("text", self.S["menu"].format(name=self.name)),
            ("prompt", self.S["menu_prompt"]),
        ]

    # -- input handlers, one per state -------------------------------

    def _in_name(self, text):
        if text.isalpha():
            self.name = text
            self.state = "level"
            return [("text", self.S["level_menu"]), ("prompt", self.S["level_prompt"])]
        return [
            ("error", self.S["invalid_name"]),
            ("prompt", self.S["name_prompt"]),
        ]

    def _in_level(self, text):
        size = LEVEL_SIZES.get(text)
        if size is None:
            return [
                ("error", self.S["invalid_level"]),
                ("prompt", self.S["level_prompt"]),
            ]
        return self._new_game(size)

    def _read_coord(self, text, field):
        """Validates one coordinate. Returns an error output list or None."""
        prompt = self.S["choose_row"] if field == "row" else self.S["choose_col"]
        if not text.isdigit():
            return [
                (
                    "error",
                    self.S["invalid_coord"].format(name=self.name, max=self.size - 1),
                ),
                ("prompt", prompt),
            ]
        value = int(text)
        if value not in range(self.size):
            return [
                ("error", self.S["out_of_map"].format(name=self.name)),
                ("prompt", prompt),
            ]
        return None

    def _in_row(self, text):
        error = self._read_coord(text, "row")
        if error is not None:
            return error
        self._row = int(text)
        self.state = "col"
        return [("prompt", self.S["choose_col"])]

    def _in_col(self, text):
        error = self._read_coord(text, "column")
        if error is not None:
            return error
        row, col = self._row, int(text)

        if self.board[row][col] == "X":
            self.state = "row"
            return [
                ("error", self.S["already_explored"].format(name=self.name)),
                ("prompt", self.S["choose_row"]),
            ]

        if row == self.chest_row and col == self.chest_col:
            self.board[row][col] = "T"
            return [
                ("board", board_text(self.board)),
                ("art", self.S["win_art"]),
                ("success", self.S["win"].format(name=self.name)),
            ] + self._menu()

        out = [("text", self.S["miss"].format(name=self.name))]
        self.board[row][col] = "X"

        if self.guess_num >= self.max_guesses:
            self.board[self.chest_row][self.chest_col] = "T"
            out += [
                ("board", board_text(self.board)),
                ("art", self.S["loss_art"]),
                ("error", self.S["lose"].format(name=self.name)),
                (
                    "text",
                    self.S["reveal"].format(row=self.chest_row, col=self.chest_col),
                ),
            ]
            return out + self._menu()

        self.guess_num += 1
        self.state = "row"
        return out + self._round_prompt()

    def _in_menu(self, text):
        choice = text.strip().upper()
        if choice == "R":
            # P0 fix: replay the SAME match - same board size and the
            # same treasure location. The old restart asked for a new
            # difficulty and hid a new treasure instead.
            out = [("text", self.S["menu_replay"])]
            return out + self._new_game(self.size, chest=(self.chest_row, self.chest_col))
        if choice == "N":
            self.state = "level"
            return [("text", self.S["level_menu"]), ("prompt", self.S["level_prompt"])]
        if choice in self.S["quit_keys"]:
            self.state = "done"
            return [("text", self.S["farewell"])]
        return [
            ("error", self.S["invalid_menu"]),
            ("prompt", self.S["menu_prompt"]),
        ]
