import re

import check50
import check50.c


@check50.check()
def exists():
    """stack.c exists"""
    check50.exists("stack.c")


@check50.check(exists)
def compiles():
    """stack.c compiles"""
    check50.c.compile("stack.c", lcs50=True)


@check50.check(compiles)
def empty_stack():
    """prints an empty stack, and pop and top say it is empty"""
    (
        menu("2", "3", "4", "0")
        .stdout(*stack())
        .stdout(*line("Stack ist leer."))
        .stdout(*line("Stack ist leer."))
        .exit(0)
    )


@check50.check(compiles)
def push():
    """prints pushed numbers, the last one first"""
    menu(*push_all(5, 9, 2), "2", "0").stdout(*stack(2, 9, 5)).exit(0)


@check50.check(compiles)
def top():
    """top shows the top number and leaves the stack unchanged"""
    (
        menu(*push_all(5, 9), "4", "4", "2", "0")
        .stdout(*line("Top: 9"))
        .stdout(*line("Top: 9"))
        .stdout(*stack(9, 5))
        .exit(0)
    )


@check50.check(compiles)
def pop():
    """pop shows and removes the top number"""
    (
        menu(*push_all(5, 9), "3", "2", "4", "0")
        .stdout(*line("Pop: 9"))
        .stdout(*stack(5))
        .stdout(*line("Top: 5"))
        .exit(0)
    )


@check50.check(compiles)
def pop_to_empty():
    """pops the last number, then pushes again"""
    (
        menu(*push_all(5, 9), "3", "3", "2", "3", *push_all(7), "2", "4", "0")
        .stdout(*line("Pop: 9"))
        .stdout(*line("Pop: 5"))
        .stdout(*stack())
        .stdout(*line("Stack ist leer."))
        .stdout(*stack(7))
        .stdout(*line("Top: 7"))
        .exit(0)
    )


@check50.check(compiles)
def clear():
    """clears the stack, then pushes again"""
    (
        menu(*push_all(5, 9), "5", "2", "4", *push_all(3), "2", "0")
        .stdout(*line("Stack geleert."))
        .stdout(*stack())
        .stdout(*line("Stack ist leer."))
        .stdout(*stack(3))
        .exit(0)
    )


@check50.check(compiles)
def negative_one():
    """handles -1 as a value"""
    (
        menu(*push_all(-1), "4", "3", "4", "0")
        .stdout(*line("Top: -1"))
        .stdout(*line("Pop: -1"))
        .stdout(*line("Stack ist leer."))
        .exit(0)
    )


@check50.check(compiles)
def invalid_choice():
    """rejects an invalid menu choice"""
    menu("9", "0").stdout(*line("Ungültige Auswahl.")).exit(0)


@check50.check(compiles)
def ends():
    """ends with 0"""
    menu("0").stdout(*line("Programm beendet.")).exit(0)


@check50.check(compiles)
def memory():
    """frees all memory"""
    program = check50.c.valgrind("./stack")

    # Popping to empty before clearing catches a head left pointing at a freed node.
    for entry in [*push_all(4, 7), "3", "3", *push_all(10, 12), "3", "5", *push_all(3, 5), "0"]:
        program.stdin(entry, prompt=False)

    program.exit(0, timeout=20)


def menu(*inputs):
    """The program, with *inputs* sent one per line."""
    program = check50.run("./stack")

    for entry in inputs:
        program.stdin(entry, prompt=False)

    return program


def push_all(*values):
    """The menu inputs that push *values*, in order."""
    return [entry for value in values for entry in ("1", str(value))]


def line(text):
    """A line of output: *text*, then the end of the line."""
    return re.escape(text) + r"[ \t]*" + "\n", text


def stack(*values):
    """The line `print_stack` prints for *values*, top first."""
    label = "Stack (oben -> unten):"
    pattern = re.escape(label) + "".join(rf"[ \t]+{value}" for value in values) + r"[ \t]*" + "\n"

    return pattern, " ".join([label, *map(str, values)])
