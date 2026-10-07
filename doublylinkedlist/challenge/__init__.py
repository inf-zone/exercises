import check50
import check50.c

# The problem's own checks, for their helpers. Never `import *` from it: its
# checks would then run as the challenge's too.
problem = check50.import_checks("..")


@check50.check()
def exists():
    """doublylinkedlist.c exists"""
    check50.exists("doublylinkedlist.c")


@check50.check(exists)
def compiles():
    """doublylinkedlist.c compiles"""
    check50.c.compile("doublylinkedlist.c", lcs50=True)


@check50.check(compiles)
def sorted_forward():
    """inserts numbers in ascending order, printed forwards"""
    problem.menu(*problem.insert(10, 4, 7), "2", "0").stdout(*problem.forward(4, 7, 10)).exit(0)


@check50.check(compiles)
def sorted_backward():
    """inserts numbers in ascending order, printed backwards"""
    problem.menu(*problem.insert(10, 4, 7), "3", "0").stdout(*problem.backward(10, 7, 4)).exit(0)


@check50.check(compiles)
def insert_front_and_back():
    """inserts before the first and after the last node"""
    (
        problem.menu(*problem.insert(5, 1, 9), "2", "3", "0")
        .stdout(*problem.forward(1, 5, 9))
        .stdout(*problem.backward(9, 5, 1))
        .exit(0)
    )


@check50.check(compiles)
def insert_duplicates():
    """keeps equal numbers next to each other"""
    problem.menu(*problem.insert(3, 8, 3, 1), "2", "0").stdout(*problem.forward(1, 3, 3, 8)).exit(0)


@check50.check(compiles)
def delete_still_works():
    """still deletes a node, then inserts in order again"""
    (
        problem.menu(*problem.insert(6, 2, 4), "5", "4", *problem.insert(5, 1), "2", "3", "0")
        .stdout(*problem.line("4 gelöscht."))
        .stdout(*problem.forward(1, 2, 5, 6))
        .stdout(*problem.backward(6, 5, 2, 1))
        .exit(0)
    )


@check50.check(compiles)
def memory():
    """frees all memory"""
    program = check50.c.valgrind("./doublylinkedlist")

    inputs = [*problem.insert(7, 4, 12, 10), "5", "7", "5", "12", "6", *problem.insert(5, 3), "0"]
    for entry in inputs:
        program.stdin(entry, prompt=False)

    program.exit(0, timeout=20)
