"""Treasure Hunt revival test suite.

Same coverage the CLI version had, now against the shared engine plus
the real CLI as a subprocess:
- 30 scripted wins
- 30 scripted losses
- 600 fuzzed rounds across 9 input classes
- restart (replay-same-map) semantics
- clean EOF / invalid-input handling, engine and CLI level
"""

import random
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from treasure_hunt import LEVEL_SIZES, TreasureHunt  # noqa: E402

SIZE_TO_LEVEL = {size: key for key, size in LEVEL_SIZES.items()}
NAMES = ["Iuri", "Ada", "Grace", "Linus", "Edsger", "Katherine"]


def collect(game, inputs):
    out = []
    for value in inputs:
        out.extend(game.submit(value))
        if game.state == "done":
            break
    return out


def joined(out):
    return "\n".join(text for _, text in out)


# ---------------------------------------------------------------- wins

WIN_CASES = []
for i in range(30):
    size = (3, 5, 9)[i % 3]
    WIN_CASES.append((NAMES[i % len(NAMES)], size, (i % size, (i * 2 + 1) % size)))


@pytest.mark.parametrize("name,size,chest", WIN_CASES)
def test_win(name, size, chest):
    game = TreasureHunt(rng=random.Random(0))
    game.start()
    out = collect(game, [name, SIZE_TO_LEVEL[size]])
    game.chest_row, game.chest_col = chest  # scripted chest placement
    out += collect(game, [str(chest[0]), str(chest[1])])
    text = joined(out)
    assert game.state == "menu"
    assert f"Congratulations explorer {name}! You found the treasure!" in text
    assert "Guess 1 of" in text  # won on the first guess


# -------------------------------------------------------------- defeats

LOSS_CASES = []
for i in range(30):
    size = (3, 5, 9)[i % 3]
    LOSS_CASES.append((NAMES[(i + 3) % len(NAMES)], size, (i % size, i % size)))


@pytest.mark.parametrize("name,size,chest", LOSS_CASES)
def test_loss(name, size, chest):
    game = TreasureHunt(rng=random.Random(0))
    game.start()
    collect(game, [name, SIZE_TO_LEVEL[size]])
    game.chest_row, game.chest_col = chest  # scripted chest placement
    max_guesses = int(size * 1.5)
    misses = [
        (r, c)
        for r in range(size)
        for c in range(size)
        if (r, c) != chest
    ][:max_guesses]
    assert len(misses) == max_guesses  # board always has enough safe cells

    inputs = []
    for r, c in misses:
        inputs += [str(r), str(c)]
    out = collect(game, inputs)
    text = joined(out)
    assert game.state == "menu"
    assert f"Sorry, explorer {name}. You didn't find the treasure this time." in text
    assert f"The treasure was hidden in location ({chest[0]}, {chest[1]})." in text


# ---------------------------------------------------- restart semantics

def test_replay_same_map_keeps_treasure():
    """P0 fix: R replays the SAME match - same size, same chest."""
    game = TreasureHunt(rng=random.Random(7))
    game.start()
    collect(game, ["Iuri", "1"])
    chest = (game.chest_row, game.chest_col)
    out = collect(game, [str(chest[0]), str(chest[1])])
    assert "Congratulations" in joined(out)

    out = collect(game, ["R"])
    assert game.state == "row"
    assert game.size == 3
    assert (game.chest_row, game.chest_col) == chest  # same map
    assert game.guess_num == 1
    assert all(cell == "-" for row in game.board for cell in row)

    out = collect(game, [str(chest[0]), str(chest[1])])
    assert "Congratulations" in joined(out)  # same spot wins again


def test_new_adventure_asks_difficulty_and_quit_is_clean():
    game = TreasureHunt(rng=random.Random(7))
    game.start()
    collect(game, ["Iuri", "1"])
    chest = (game.chest_row, game.chest_col)
    collect(game, [str(chest[0]), str(chest[1])])

    out = collect(game, ["N"])
    assert game.state == "level"
    assert "difficulty level" in joined(out)

    collect(game, ["2"])
    assert game.size == 5

    # finish the second game with a win, then quit
    chest2 = (game.chest_row, game.chest_col)
    collect(game, [str(chest2[0]), str(chest2[1])])
    out = collect(game, ["Q"])
    assert game.state == "done"
    assert "Thanks for playing! Come back soon!" in joined(out)


def test_menu_rejects_garbage():
    game = TreasureHunt(rng=random.Random(7))
    game.start()
    collect(game, ["Iuri", "1"])
    chest = (game.chest_row, game.chest_col)
    collect(game, [str(chest[0]), str(chest[1])])
    for bad in ["", "X", "yes", "12", "rr"]:
        out = collect(game, [bad])
        assert "Invalid input. Please, enter R, N or Q." in joined(out)
        assert game.state == "menu"


# --------------------------------------------------------- EOF handling

def test_eof_from_every_state_is_clean():
    for setup in (0, 1, 2, 3, 4):
        game = TreasureHunt(rng=random.Random(7))
        game.start()
        script = ["Iuri", "1", "0", "0"][:setup]
        collect(game, script)
        out = game.eof()
        assert game.state == "done"
        text = joined(out)
        assert "Input closed" in text and "Thanks for playing" in text


# --------------------------------------------------------------- fuzz

FUZZ_CLASSES = (
    "valid", "nondigit", "empty", "negative", "out_of_range",
    "repeat", "whitespace", "huge", "unicode",
)


def fuzz_value(cls, size, last_guess, rng):
    if cls == "valid":
        return str(rng.randrange(size))
    if cls == "nondigit":
        return rng.choice(["abc", "1a", "x", "row2", "."])
    if cls == "empty":
        return ""
    if cls == "negative":
        return str(-rng.randrange(1, 100))
    if cls == "out_of_range":
        return str(rng.randrange(size, size + 500))
    if cls == "repeat":
        return last_guess if last_guess is not None else "0"
    if cls == "whitespace":
        return rng.choice([" ", "   ", "\t", " 2 "])
    if cls == "huge":
        return "9" * rng.randrange(10, 40)
    if cls == "unicode":
        return rng.choice(["é", "🌟", "º", "ß", "🎲"])
    raise AssertionError(cls)


def test_fuzz_600_rounds_9_input_classes():
    """600 completed guess rounds; garbage never consumes a guess,
    no input ever crashes the engine or corrupts its state."""
    rng = random.Random(20260930)
    game = TreasureHunt(rng=random.Random(rng.randrange(10**9)))
    game.start()
    collect(game, ["Fuzzer", "1"])

    rounds = 0
    games = 1
    wins = 0
    losses = 0
    steps = 0
    last_guess = None

    while rounds < 600:
        steps += 1
        assert steps < 100000, "fuzz made no progress"

        if game.state == "done":
            games += 1
            game = TreasureHunt(rng=random.Random(rng.randrange(10**9)))
            game.start()
            collect(game, ["Fuzzer", rng.choice(["1", "2", "3"])])
            last_guess = None
            continue

        if game.state == "menu":
            before = "\n".join(t for _, t in game_history) if False else ""
            choice = rng.choice(["R", "N", "Q"])
            collect(game, [choice])
            if choice == "N":
                collect(game, [rng.choice(["1", "2", "3"])])
            last_guess = None
            continue

        assert game.state in ("row", "col"), f"unexpected state {game.state}"
        cls = FUZZ_CLASSES[rng.randrange(len(FUZZ_CLASSES))]
        value = fuzz_value(cls, game.size, last_guess, rng)
        guesses_before = game.guess_num
        state_before = game.state

        out = game.submit(value)  # must never raise

        assert game.state in TreasureHunt.STATES
        assert 1 <= game.guess_num <= game.max_guesses

        if cls != "valid" or state_before == "col" and game.state == "col":
            # invalid coordinate input never advances the round
            if cls in ("nondigit", "empty", "negative", "out_of_range",
                       "whitespace", "huge", "unicode"):
                assert game.guess_num == guesses_before, cls

        if state_before == "col" and game.state != "col":
            # a column answer closed the round one way or another
            rounds += 1
            text = joined(out)
            if "Congratulations" in text:
                wins += 1
            elif "didn't find the treasure" in text:
                losses += 1
        if state_before == "row" and game.state == "col":
            last_guess = value

    assert rounds == 600
    assert games >= 10, f"only {games} games in 600 rounds"
    assert wins + losses >= 10
    print(f"\nfuzz: {rounds} rounds, {games} games, {wins} wins, {losses} losses")


# ------------------------------------------------- CLI subprocess level

def run_cli(stdin_text, env_extra=None, timeout=20):
    import os
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, str(ROOT / "run.py")],
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def test_cli_eof_immediately_is_clean():
    """P0: Ctrl+D at the first prompt - no traceback, exit code 0."""
    proc = run_cli("")
    assert proc.returncode == 0
    assert "Traceback" not in proc.stderr
    assert "Input closed" in proc.stdout
    assert "Thanks for playing" in proc.stdout


def test_cli_eof_mid_game_is_clean():
    proc = run_cli("Iuri\n1\n0\n")
    assert proc.returncode == 0
    assert "Traceback" not in proc.stderr
    assert "Input closed" in proc.stdout


def test_cli_garbage_then_eof_never_crashes():
    proc = run_cli("John Doe\nIuri\n5\n3\nabc\n-1\n99\n\n \n0\n0\n")
    assert proc.returncode == 0
    assert "Traceback" not in proc.stderr
    assert "Invalid name" in proc.stdout
    assert "Invalid choice" in proc.stdout
    assert "Invalid option" in proc.stdout


def test_cli_full_win_with_seed():
    """Deterministic end-to-end win through the real CLI."""
    seed = 42
    probe = random.Random(seed)
    chest = (probe.randrange(3), probe.randrange(3))
    script = f"Iuri\n1\n{chest[0]}\n{chest[1]}\nQ\n"
    proc = run_cli(script, env_extra={"TREASURE_HUNT_SEED": str(seed)})
    assert proc.returncode == 0
    assert "Traceback" not in proc.stderr
    assert "Congratulations explorer Iuri! You found the treasure!" in proc.stdout
    assert "Thanks for playing! Come back soon!" in proc.stdout


def test_cli_replay_same_map_wins_again():
    seed = 42
    probe = random.Random(seed)
    chest = (probe.randrange(3), probe.randrange(3))
    script = f"Iuri\n1\n{chest[0]}\n{chest[1]}\nR\n{chest[0]}\n{chest[1]}\nQ\n"
    proc = run_cli(script, env_extra={"TREASURE_HUNT_SEED": str(seed)})
    assert proc.returncode == 0
    assert proc.stdout.count("Congratulations") == 2
