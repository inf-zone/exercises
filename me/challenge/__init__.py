import re

import check50
import check50.c


@check50.check()
def exists():
    """hello.c exists"""
    check50.exists("hello.c")


@check50.check(exists)
def compiles():
    """hello.c compiles"""
    check50.c.compile("hello.c", lcs50=True)


@check50.check(compiles)
def ada():
    """greets Ada Lovelace with her full name"""
    greets("Ada", "Lovelace")


@check50.check(compiles)
def grace():
    """greets Grace Hopper with her full name"""
    greets("Grace", "Hopper")


def greets(first, last):
    name = f"{first} {last}"
    check50.run("./hello").stdin(first).stdin(last).stdout(
        rf"[Hh]ello, {re.escape(name)}" + "\n", f"hello, {name}\n"
    ).exit(0)
