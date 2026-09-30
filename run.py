#!/usr/bin/env python3
"""Treasure Hunt - terminal entry point (revival).

Thin CLI wrapper over the treasure_hunt engine. The same engine also
powers the browser version (web/, via Pyodide) and the test suite.

Audit fixes (2026-09-30):
- P0 cp1252 crash: stdout/stderr are reconfigured to UTF-8 with
  errors="replace", so the art and quotes print on any terminal.
- P0 EOF crash: Ctrl+D / Ctrl+Z / closed stdin ends the game with a
  clean farewell instead of a traceback. Ctrl+C is handled too.
- P0 restart semantics: handled inside the engine (menu option R
  replays the same map; N starts a new adventure).
- P2: no unprotected while True wrappers; the engine owns the states.

Environment hooks (used by the test suite, harmless for players):
- TREASURE_HUNT_SEED: integer seed for deterministic chest placement.
"""

import os
import random
import sys

from treasure_hunt import TreasureHunt


def _configure_streams():
    """Forces UTF-8 output so cp1252 terminals never crash on the art."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            # Very old Python or an exotic stream: printing still works,
            # only exotic characters could fail there.
            pass


def _emit(outputs):
    for kind, text in outputs:
        if kind == "prompt":
            print(text, end="", flush=True)
        else:
            print(text)


def main():
    _configure_streams()
    seed = os.environ.get("TREASURE_HUNT_SEED")
    rng = random.Random(int(seed)) if seed is not None else None
    game = TreasureHunt(rng)

    _emit(game.start())
    while game.state != "done":
        try:
            line = input()
        except EOFError:
            print()
            _emit(game.eof())
            break
        except KeyboardInterrupt:
            print()
            _emit(game.interrupt())
            break
        _emit(game.submit(line))
    return 0


if __name__ == "__main__":
    sys.exit(main())
