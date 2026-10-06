import re

import check50
import check50.c


@check50.check()
def exists():
    """doublylinkedlist.c exists"""
    check50.exists("doublylinkedlist.c")


@check50.check(exists)
def compiles():
    """doublylinkedlist.c compiles"""
    check50.c.compile("doublylinkedlist.c", lcs50=True)


@check50.check(compiles)
def empty_list():
    """prints an empty list forwards and backwards"""
    menu("2", "3", "0").stdout(*forward()).stdout(*backward()).exit(0)


@check50.check(compiles)
def insert_forward():
    """prints inserted numbers forwards"""
    menu(*insert(4, 7, 10), "2", "0").stdout(*forward(4, 7, 10)).exit(0)


@check50.check(compiles)
def insert_backward():
    """prints inserted numbers backwards"""
    menu(*insert(4, 7, 10), "3", "0").stdout(*backward(10, 7, 4)).exit(0)


@check50.check(compiles)
def search_found():
    """finds a value in the list"""
    menu(*insert(5, 9), "4", "9", "0").stdout(*line("9 wurde gefunden.")).exit(0)


@check50.check(compiles)
def search_missing():
    """does not find a value missing from the list"""
    menu(*insert(5, 9), "4", "3", "0").stdout(*line("3 nicht in der Liste.")).exit(0)


@check50.check(compiles)
def delete_middle():
    """deletes a node in the middle"""
    (
        menu(*insert(4, 7, 10), "5", "7", "2", "3", "0")
        .stdout(*line("7 gelöscht."))
        .stdout(*forward(4, 10))
        .stdout(*backward(10, 4))
        .exit(0)
    )


@check50.check(compiles)
def delete_first():
    """deletes the first node"""
    (
        menu(*insert(4, 7, 10), "5", "4", "2", "3", "0")
        .stdout(*line("4 gelöscht."))
        .stdout(*forward(7, 10))
        .stdout(*backward(10, 7))
        .exit(0)
    )


@check50.check(compiles)
def delete_last():
    """deletes the last node"""
    (
        menu(*insert(4, 7, 10), "5", "10", "2", "3", "0")
        .stdout(*line("10 gelöscht."))
        .stdout(*forward(4, 7))
        .stdout(*backward(7, 4))
        .exit(0)
    )


@check50.check(compiles)
def delete_only():
    """deletes the only node, then inserts again"""
    (
        menu(*insert(5), "5", "5", "2", "3", *insert(6), "2", "3", "0")
        .stdout(*line("5 gelöscht."))
        .stdout(*forward())
        .stdout(*backward())
        .stdout(*forward(6))
        .stdout(*backward(6))
        .exit(0)
    )


@check50.check(compiles)
def delete_missing():
    """leaves the list unchanged when deleting a missing value"""
    (
        menu(*insert(4, 7), "5", "3", "2", "3", "0")
        .stdout(*line("3 nicht gefunden."))
        .stdout(*forward(4, 7))
        .stdout(*backward(7, 4))
        .exit(0)
    )


@check50.check(compiles)
def clear():
    """clears the list, then inserts again"""
    (
        menu(*insert(4, 7), "6", "2", *insert(8), "2", "3", "0")
        .stdout(*line("Liste geleert."))
        .stdout(*forward())
        .stdout(*forward(8))
        .stdout(*backward(8))
        .exit(0)
    )


@check50.check(compiles)
def invalid_choice():
    """rejects an invalid menu choice"""
    menu("9", "0").stdout(*line("Ungültige Auswahl. Bitte erneut versuchen.")).exit(0)


@check50.check(compiles)
def ends():
    """ends with 0"""
    menu("0").stdout(*line("Programm beendet.")).exit(0)


@check50.check(compiles)
def memory():
    """frees all memory"""
    program = check50.c.valgrind("./doublylinkedlist")

    for entry in [*insert(4, 7, 10, 12), "5", "7", "5", "12", "6", *insert(3, 5), "0"]:
        program.stdin(entry, prompt=False)

    program.exit(0, timeout=20)


def menu(*inputs):
    """The program, with *inputs* sent one per line."""
    program = check50.run("./doublylinkedlist")

    for entry in inputs:
        program.stdin(entry, prompt=False)

    return program


def insert(*values):
    """The menu inputs that insert *values*, in order."""
    return [entry for value in values for entry in ("1", str(value))]


def line(text):
    """A line of output: *text*, then the end of the line."""
    return re.escape(text) + r"[ \t]*" + "\n", text


def forward(*values):
    """The line `print_forward` prints for *values*."""
    return numbers("Vorwärts:", values)


def backward(*values):
    """The line `print_backward` prints for *values*."""
    return numbers("Rückwärts:", values)


def numbers(label, values):
    """A line of *label* and *values*, separated by spaces, with any trailing spaces."""
    pattern = re.escape(label) + "".join(rf"[ \t]+{value}" for value in values) + r"[ \t]*" + "\n"

    return pattern, " ".join([label, *map(str, values)])
