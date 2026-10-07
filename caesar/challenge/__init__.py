import re

import check50
import check50.c


@check50.check()
def exists():
    """caesar.c exists."""
    check50.exists("caesar.c")


@check50.check(exists)
def compiles():
    """caesar.c compiles."""
    check50.c.compile("caesar.c", lcs50=True)


@check50.check(compiles)
def decrypts_b_as_a():
    """encrypts "b" as "a" using -1 as key"""
    encrypts("-1", "b", "a")


@check50.check(compiles)
def decrypts_a_as_z():
    """encrypts "a" as "z" using -1 as key"""
    encrypts("-1", "a", "z")


@check50.check(compiles)
def decrypts_mixed():
    """encrypts "Ebiil, Tloia!" as "Hello, World!" using -23 as key"""
    encrypts("-23", "Ebiil, Tloia!", "Hello, World!")


@check50.check(compiles)
def decrypts_large():
    """encrypts "onesbb" as "barfoo" using -65 as key"""
    encrypts("-65", "onesbb", "barfoo")


@check50.check(compiles)
def still_encrypts():
    """still encrypts "barfoo" as "yxocll" using 23 as key"""
    encrypts("23", "barfoo", "yxocll")


@check50.check(compiles)
def handles_minus_alone():
    """handles a key of only "-" """
    check50.run("./caesar -").exit(1)


@check50.check(compiles)
def handles_non_numeric_argv():
    """still handles non-numeric key"""
    check50.run("./caesar -2x").exit(1)


def encrypts(key, plaintext, ciphertext):
    check50.run(f"./caesar {key}").stdin(plaintext).stdout(
        rf"[Cc]iphertext:\s*{re.escape(ciphertext)}" + "\n", f"ciphertext: {ciphertext}\n"
    ).exit(0)
