import re

import check50
import check50.c


@check50.check()
def exists():
    """stadtlandfluss.c exists"""
    check50.exists("stadtlandfluss.c")


@check50.check(exists)
def compiles():
    """stadtlandfluss.c compiles"""
    check50.c.compile("stadtlandfluss.c", lcs50=True)


@check50.check(compiles)
def one_number():
    """prints A for the number 1"""
    letter("1", "A")


@check50.check(compiles)
def wraps_around():
    """prints A for the number 27"""
    letter("27", "A")


@check50.check(compiles)
def two_numbers():
    """prints A for the numbers 10 and 17"""
    letter("10 17", "A")


@check50.check(compiles)
def three_numbers():
    """prints C for the numbers 1, 1 and 1"""
    letter("1 1 1", "C")


@check50.check(compiles)
def eight_numbers():
    """prints H for eight times the number 1"""
    letter("1 1 1 1 1 1 1 1", "H")


@check50.check(compiles)
def large_sum():
    """prints Z for the numbers 26 and 26"""
    letter("26 26", "Z")


@check50.check(compiles)
def rejects_negative():
    """rejects the numbers 1 and -1"""
    rejected("1 -1")


@check50.check(compiles)
def rejects_letters():
    """rejects the arguments A and B"""
    rejected("A B")


@check50.check(compiles)
def rejects_no_numbers():
    """rejects being run without numbers"""
    rejected("")


@check50.check(compiles)
def rejects_nine_numbers():
    """rejects nine numbers"""
    rejected("1 2 3 4 5 6 7 8 9")


def letter(arguments, expected):
    """Runs the program with *arguments* and expects *expected* on a line of its own."""
    check50.run(f"./stadtlandfluss {arguments}").stdout(f"^{expected}\n", f"{expected}\n").exit(0)


def rejected(arguments):
    """Runs the program with *arguments* and expects an error message, not a letter."""
    output = check50.run(f"./stadtlandfluss {arguments}".strip()).stdout()

    if not output.strip():
        raise check50.Failure("expected an error message, but the program printed nothing")

    if re.fullmatch(r"\s*\S\s*", output):
        raise check50.Mismatch("an error message", output)
