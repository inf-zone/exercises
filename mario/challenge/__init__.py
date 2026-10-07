import check50
import check50.c

# The problem's own checks, for their helpers. Never `import *` from it: its
# checks would then run as the challenge's too.
problem = check50.import_checks("..")


@check50.check()
def exists():
    """mario.c exists"""
    check50.exists("mario.c")


@check50.check(exists)
def compiles():
    """mario.c compiles"""
    check50.c.compile("mario.c", lcs50=True)


@check50.check(compiles)
def test1():
    """prints a pyramid of height 1 with dots in its bottom row"""
    out = check50.run("./mario").stdin("1").stdout()
    problem.check_pyramid(out, pyramid(1))


@check50.check(compiles)
def test2():
    """prints a pyramid of height 2 with dots in its bottom row"""
    out = check50.run("./mario").stdin("2").stdout()
    problem.check_pyramid(out, pyramid(2))


@check50.check(compiles)
def test8():
    """prints a pyramid of height 8 with dots in its bottom row"""
    out = check50.run("./mario").stdin("8").stdout()
    problem.check_pyramid(out, pyramid(8))


@check50.check(compiles)
def test_reject_then_accept():
    """still rejects a height of 0, and then accepts a height of 3"""
    out = check50.run("./mario").stdin("0").reject().stdin("3").stdout()
    problem.check_pyramid(out, pyramid(3))


def pyramid(height):
    """The pyramid of *height*: hashes, but dots in the bottom row."""
    rows = [" " * (height - row) + "#" * row for row in range(1, height)]
    rows.append("." * height)

    return "\n".join(rows) + "\n"
