import check50
import check50.c
import re

# The problem's own checks, for their helpers. Never `import *` from it: its
# checks would then run as the challenge's too.
problem = check50.import_checks("..")


@check50.check()
def exists():
    """plurality.c exists"""
    check50.exists("plurality.c")

    check50.include("../testing.c")


@check50.check(exists)
def compiles():
    """plurality compiles"""
    check50.c.compile("plurality.c", lcs50=True)

    # The functions without main, and the harness's main that calls them.
    plurality = re.sub(r"int\s+main", "int distro_main", open("plurality.c").read())
    testing = open("testing.c").read()
    with open("plurality_test.c", "w") as f:
        f.write(plurality)
        f.write("\n")
        f.write(testing)

    check50.c.compile("plurality_test.c", lcs50=True)


@check50.check(compiles)
def single_winner_first():
    """print_winner still identifies Alice as winner of election"""
    problem.check_winner(check50.run("./plurality_test 0 7").stdout(), "Alice\n")


@check50.check(compiles)
def single_winner_last():
    """print_winner still identifies Charlie as winner of election"""
    problem.check_winner(check50.run("./plurality_test 0 9").stdout(), "Charlie\n")


@check50.check(compiles)
def tie_of_two():
    """print_winner prints "Tie!" when Alice and Bob are tied"""
    problem.check_winner(check50.run("./plurality_test 0 10").stdout(), "Tie!\n")


@check50.check(compiles)
def tie_of_all():
    """print_winner prints "Tie!" when all candidates are tied"""
    problem.check_winner(check50.run("./plurality_test 0 11").stdout(), "Tie!\n")
