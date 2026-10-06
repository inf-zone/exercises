import re
import time

import check50
import check50.c

ROUND = re.compile(r"Runde\s+(\d+)\s*:\s*([A-Za-z])")


@check50.check()
def exists():
    """stadtlandfluss2.c exists"""
    check50.exists("stadtlandfluss2.c")


@check50.check(exists)
def compiles():
    """stadtlandfluss2.c compiles"""
    check50.c.compile("stadtlandfluss2.c", lcs50=True)


@check50.check(compiles)
def first_round():
    """prints "Runde 1" and a letter after an empty input"""
    output = answer("", "Ende")
    rounds = ROUND.findall(output)

    if len(rounds) != 1 or rounds[0][0] != "1":
        raise check50.Mismatch("Runde 1: X", output)


@check50.check(compiles)
def any_input():
    """starts a new round after any other input"""
    output = answer("Hallo", "sdfjhk", "x")
    rounds = [number for number, _ in ROUND.findall(output)]

    if rounds != ["1", "2"]:
        raise check50.Mismatch("Runde 1: X\n...Runde 2: Y", output)


@check50.check(compiles)
def ends_with_ende():
    '''ends after the input "Ende"'''
    stops("Ende")


@check50.check(compiles)
def ends_with_x():
    '''ends after the input "x"'''
    stops("x")


@check50.check(compiles)
def twenty_six_rounds():
    """prints each letter once in 26 rounds, then ends"""
    letters = play()

    if len(set(letters)) != 26:
        repeated = sorted({letter for letter in letters if letters.count(letter) > 1})
        raise check50.Failure(
            f"expected 26 different letters, but {', '.join(repeated)} came more than once"
        )


@check50.check(twenty_six_rounds)
def different_runs():
    """prints the letters in a different order on every run"""
    first = play()

    # srand(time(NULL)) changes its seed once a second.
    time.sleep(1.1)
    second = play()

    if first == second:
        raise check50.Failure(
            f"expected two runs to print different letters, but both printed {''.join(first)}",
            help="Did you call srand once, with the current time?",
        )


def stops(word):
    """Plays one round, then expects the program to end after *word* without another round."""
    output = answer("", word)
    rounds = [number for number, _ in ROUND.findall(output)]

    if rounds != ["1"]:
        raise check50.Mismatch("Runde 1: X", output)


def answer(*lines):
    """Runs the program with *lines* as input and returns all it printed until it ended."""
    program = check50.run("./stadtlandfluss2")

    for line in lines:
        program.stdin(line, prompt=False)

    return program.stdout(timeout=5)


def play():
    """Plays 26 rounds and returns the letters in order, checking rounds 1 to 26 and the end."""
    output = answer(*[""] * 26)
    rounds = ROUND.findall(output)
    numbers = [int(number) for number, _ in rounds]

    if numbers != list(range(1, 27)):
        raise check50.Failure(
            f"expected rounds 1 to 26, but found {', '.join(map(str, numbers)) or 'none'}"
        )

    return [letter.upper() for _, letter in rounds]
