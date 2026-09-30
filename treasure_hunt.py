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
"""

import random

BANNER = '******************************************************************\n                   |                 |                     |\n________________.="";=.______________|_____________________|_____\n         |  ,-"_,=""     `"=.|                  |\n_________|__"=._o`"-._        `"=.______________|________________\n                `"=._o`"=._      _`"=._                     |\n_____________________:=._o "=._."_.-="\'"=.__________________|____\n         |    __.--" , ; `"=._o." ,-"""-._ ".   |\n_________|_._"  ,. .` ` `` ,  `"-._"-._   ". \'__|________________\n           |o`"=._` , "` `; .". ,  "-._"-._; ;              |\n___________| ;`-.o`"=._; ." ` \'"`.\\` . "-._ /_______________|____\n         | |o;    `"-.o`"=._``  \'"` " ,__.--o;  |\n_________|_| ;     (#) `-.o `"=.`_.--"_o.-; ;___|_________________\n/______/___|o;._    "      `".o|o_.--"    ;o;____/______/______/__\n___/______/_"=._o--._        ; | ;        ; ;/______/______/______\n/______/______/__"=._o--._   ;o|o;     _._;o;____/______/______/__\n___/______/______/____"=._o._; | ;_.--"o.--"_/______/______/______\n/______/______/______/______"=.o|o_.--""___/______/______/______/_\n___/______/______/______/______/______/______/______/______/______\n   ).-.o.*)    +-+-+-+-+-+-+-+-+ +-+-+-+-+ +-+-+-+-+    ).-.o.*)\n  (:_.:.*(     |T|r|e|a|s|u|r|e| |H|u|n|t| |G|a|m|e|   (:_.:.*(\n   )*.-.o.)                                             )*.-.o.)\n  (-X_.*:(             |b|y| |i|u|r|j|o|h|             (-X_.*:(\n   )-.--.*)    +-+-+-+ +-+-+ +-+-+-+-+-+-+ +-+-+-+-+    )-.--.*)                          \n'

WIN_ART = '                ______\n             .-\'      `-.\n           .\'            `.\n          /                \\.\n         ;                 ;`\n         |          /      |;\n         ;         / / /   ;|\n         \'\\       / / /   / ;\n          \\`.    / /    .\' /\n           `.`-._____.-\' .\'\n             / /`_____.-\'\n            / / /\n           / / /    \n          / / /    "History may be accurate.\n         / / /       \n        / / /       But archaeology is precise."\n       / / /         \n      / / /         ― Doug Scott\n     / / /\n    / / /\n    \\/_/                          \n'

LOSS_ART = '\n         ,---,_          ,\n          _>   `\'-.  .--\'/\n     .--\'` ._      `/   <_\n      >,-\' ._\'.. ..__ . \' \'-.       "Failure\n   .-\'   .\'`         `\'.     \'.\n    >   / >`-.     .-\'< \\ , \'._\\.    is success\n   /    ; \'-._>   <_.-\' ;  \'._>\n   `>  ,/  /___\\ /___\\  \\_  /        in progress."\n   `.-|(|  \\_o/  \\_o/   |)|`\n       \\;        \\      ;/           ― Albert Einstein\n         \\  .-,   )-.  /\n          /`  .\'-\'.  `\\.\n         ;_.-`.___.\'-.;\n'

VALID_SIZES = (3, 5, 9)
LEVEL_SIZES = {"1": 3, "2": 5, "3": 9}

LEVEL_MENU = (
    "Please, choose your difficulty level:\n"
    "1. Easy (board size: 3x3)\n"
    "2. Medium (board size: 5x5)\n"
    "3. Hard (board size: 9x9)"
)

NAME_PROMPT = "Welcome explorer! Please, enter your name (only letters): "
LEVEL_PROMPT = "Enter your choice (1-3): "
FAREWELL = "Thanks for playing! Come back soon!"


def board_text(board):
    """Renders the 2D board exactly like the original CLI did."""
    size = len(board)
    lines = ["   " + " ".join(str(col) for col in range(size))]
    for row in range(size):
        lines.append(f"{row}  " + " ".join(board[row]))
    return "\n".join(lines)


class TreasureHunt:
    """One Treasure Hunt session. Drive it with start()/submit()/eof()."""

    STATES = ("name", "level", "row", "col", "menu", "done")

    def __init__(self, rng=None):
        self.rng = rng if rng is not None else random.Random()
        self.state = "name"
        self.name = None
        self.size = None
        self.board = None
        self.chest_row = None
        self.chest_col = None
        self.max_guesses = 0
        self.guess_num = 0
        self._row = None

    def start(self):
        """First screen: banner plus the name prompt."""
        return [("art", BANNER), ("prompt", NAME_PROMPT)]

    def eof(self):
        """Clean exit on Ctrl+D / closed stdin, from any state."""
        self.state = "done"
        return [("text", f"Input closed. {FAREWELL}")]

    def interrupt(self):
        """Clean exit on Ctrl+C, from any state."""
        self.state = "done"
        return [("text", f"Interrupted. {FAREWELL}")]

    def submit(self, text):
        """Feeds one line of player input, returns (kind, text) output pairs."""
        if self.state == "done":
            return [("error", "The game is over. Reload to play again.")]
        handler = getattr(self, "_in_" + self.state)
        return handler(text)

    # -- setup ------------------------------------------------------

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
        intro = (
            f"Board size: {size}x{size}."
            f" Treasure: 1. Guesses: {self.max_guesses}."
        )
        return [("text", intro)] + self._round_prompt()

    def _round_prompt(self):
        return [
            (
                "text",
                f"Explorer {self.name}, where should we dig now?"
                f" Guess {self.guess_num} of {self.max_guesses}.",
            ),
            ("board", board_text(self.board)),
            ("prompt", "Choose a row: "),
        ]

    def _menu(self):
        self.state = "menu"
        return [
            (
                "text",
                f"Explorer {self.name}, what now?\n"
                "R - Replay the same map (same treasure location)\n"
                "N - New adventure (choose the difficulty)\n"
                "Q - Quit",
            ),
            ("prompt", "Choose (R/N/Q): "),
        ]

    # -- input handlers, one per state -------------------------------

    def _in_name(self, text):
        if text.isalpha():
            self.name = text
            self.state = "level"
            return [("text", LEVEL_MENU), ("prompt", LEVEL_PROMPT)]
        return [
            (
                "error",
                "Invalid name. Please, enter a non-empty name"
                " with only letters from A to Z.",
            ),
            ("prompt", NAME_PROMPT),
        ]

    def _in_level(self, text):
        size = LEVEL_SIZES.get(text)
        if size is None:
            return [
                ("error", "Invalid choice. Please, enter a number between 1 and 3."),
                ("prompt", LEVEL_PROMPT),
            ]
        return self._new_game(size)

    def _read_coord(self, text, field):
        """Validates one coordinate. Returns an error output list or None."""
        if not text.isdigit():
            return [
                (
                    "error",
                    f"Invalid option, explorer {self.name}."
                    f" Please, enter valid numbers between 0 and {self.size - 1}.",
                ),
                ("prompt", f"Choose a {field}: "),
            ]
        value = int(text)
        if value not in range(self.size):
            return [
                (
                    "error",
                    f"Sorry explorer {self.name},"
                    " those coordinates are outside the map.",
                ),
                ("prompt", f"Choose a {field}: "),
            ]
        return None

    def _in_row(self, text):
        error = self._read_coord(text, "row")
        if error is not None:
            return error
        self._row = int(text)
        self.state = "col"
        return [("prompt", "Choose a column: ")]

    def _in_col(self, text):
        error = self._read_coord(text, "column")
        if error is not None:
            return error
        row, col = self._row, int(text)

        if self.board[row][col] == "X":
            self.state = "row"
            return [
                (
                    "error",
                    "This location was explored."
                    f" Please, try a new one explorer {self.name}.",
                ),
                ("prompt", "Choose a row: "),
            ]

        if row == self.chest_row and col == self.chest_col:
            self.board[row][col] = "T"
            return [
                ("board", board_text(self.board)),
                ("art", WIN_ART),
                ("success", f"Congratulations explorer {self.name}! You found the treasure!"),
            ] + self._menu()

        out = [("text", f"Sorry, explorer {self.name}. You missed the treasure!")]
        self.board[row][col] = "X"

        if self.guess_num >= self.max_guesses:
            self.board[self.chest_row][self.chest_col] = "T"
            out += [
                ("board", board_text(self.board)),
                ("art", LOSS_ART),
                ("error", f"Sorry, explorer {self.name}. You didn't find the treasure this time."),
                ("text", f"The treasure was hidden in location ({self.chest_row}, {self.chest_col})."),
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
            out = [("text", "Same map, explorer. The treasure stayed where it was. Good luck!")]
            return out + self._new_game(self.size, chest=(self.chest_row, self.chest_col))
        if choice == "N":
            self.state = "level"
            return [("text", LEVEL_MENU), ("prompt", LEVEL_PROMPT)]
        if choice == "Q":
            self.state = "done"
            return [("text", FAREWELL)]
        return [
            ("error", "Invalid input. Please, enter R, N or Q."),
            ("prompt", "Choose (R/N/Q): "),
        ]
