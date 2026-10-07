import re

import check50

# Each text and its grade; the counts come from counts() below.
TEXTS = {
    "one_sentence": (
        "In my younger and more vulnerable years my father gave me some advice that I've been "
        "turning over in my mind ever since.",
        "Grade 7",
    ),
    "punctuation": (
        "There are more things in Heaven and Earth, Horatio, than are dreamt of in your "
        "philosophy.",
        "Grade 9",
    ),
    "several_sentences": (
        "Harry Potter was a highly unusual boy in many ways. For one thing, he hated the summer "
        "holidays more than any other time of year. For another, he really wanted to do his "
        "homework, but was forced to do it in secret, in the dead of the night. And he also "
        "happened to be a wizard.",
        "Grade 5",
    ),
    "before_grade_1": (
        "One fish. Two fish. Red fish. Blue fish.",
        "Before Grade 1",
    ),
}


@check50.check()
def exists():
    """readability.py exists."""
    check50.exists("readability.py")


@check50.check(exists)
def one_sentence():
    """prints the counts and the grade of a single sentence"""
    check_counts(*TEXTS["one_sentence"])


@check50.check(exists)
def punctuation():
    """prints the counts and the grade of a sentence with commas"""
    check_counts(*TEXTS["punctuation"])


@check50.check(exists)
def several_sentences():
    """prints the counts and the grade of several sentences"""
    check_counts(*TEXTS["several_sentences"])


@check50.check(exists)
def before_grade_1():
    """prints the counts before "Before Grade 1" """
    check_counts(*TEXTS["before_grade_1"])


def counts(text):
    """Letters, words and sentences of *text*, as readability counts them."""
    letters = sum(1 for char in text if char.isalpha())
    words = len(text.split())
    sentences = sum(1 for char in text if char in ".!?")

    return letters, words, sentences


def check_counts(text, grade):
    letters, words, sentences = counts(text)

    program = check50.run("python3 readability.py").stdin(text)
    for label, value in (("Letters", letters), ("Words", words), ("Sentences", sentences)):
        program.stdout(rf"{label}:[ \t]*{value}[ \t]*" + "\n", f"{label}: {value}\n")

    program.stdout(re.escape(grade) + "\n", f"{grade}\n").exit(0)
