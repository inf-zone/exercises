import check50
import check50.c

# The problem's own checks, for their helpers and sample images. Never
# `import *` from it: its checks would then run as the challenge's too.
problem = check50.import_checks("..")


@check50.check()
def exists():
    """helpers.c exists"""
    check50.exists("helpers.c")

    check50.include("../Makefile", "../bmp.h", "../helpers.h", "../testing.c")


@check50.check(exists)
def compiles():
    """filter compiles"""
    check50.run("make").exit(0)


@check50.check(compiles)
def reflect_row2():
    """reflect leaves a 1x2 image unchanged"""
    problem.log(problem.SAMPLE_IMAGES[3])
    check50.run("./testing 2 0").stdout("".join([
        "255 0 0\n", "0 0 255\n"
    ]))


@check50.check(compiles)
def reflect_row3():
    """reflect leaves a 1x3 image unchanged"""
    problem.log(problem.SAMPLE_IMAGES[4])
    check50.run("./testing 2 1").stdout("".join([
        "255 0 0\n", "0 255 0\n", "0 0 255\n"
    ]))


@check50.check(compiles)
def reflect_simple():
    """reflect turns a 3x3 image of colored rows upside down"""
    problem.log(problem.SAMPLE_IMAGES[0])
    check50.run("./testing 2 2").stdout("".join([
        "0 0 255\n", "0 0 255\n", "0 0 255\n",
        "0 255 0\n", "0 255 0\n", "0 255 0\n",
        "255 0 0\n", "255 0 0\n", "255 0 0\n"
    ]))


@check50.check(compiles)
def reflect3():
    """reflect turns a 3x3 image upside down"""
    problem.log(problem.SAMPLE_IMAGES[1])
    check50.run("./testing 2 3").stdout("".join([
        "200 210 220\n", "220 230 240\n", "240 250 255\n",
        "110 130 140\n", "120 140 150\n", "130 150 160\n",
        "10 20 30\n", "40 50 60\n", "70 80 90\n"
    ]))


@check50.check(compiles)
def reflect4():
    """reflect turns a 4x4 image upside down"""
    problem.log(problem.SAMPLE_IMAGES[2])
    check50.run("./testing 2 4").stdout("".join([
        "50 28 90\n", "0 0 0\n", "255 255 255\n", "85 85 85\n",
        "195 204 213\n", "205 214 223\n", "225 234 243\n", "245 254 253\n",
        "110 130 140\n", "120 140 150\n", "130 150 160\n", "140 160 170\n",
        "10 20 30\n", "40 50 60\n", "70 80 90\n", "100 110 120\n"
    ]))
