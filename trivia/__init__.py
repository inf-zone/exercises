import re

import check50
from bs4 import BeautifulSoup


@check50.check()
def exists():
    """index.html and styles.css exist"""
    check50.exists("index.html", "styles.css")


@check50.check(exists)
def multiple_choice():
    """Part 1 has a question in an h3 and at least three buttons"""
    section = part("Part 1")

    if section.find("h3") is None:
        raise check50.Failure("expected the question of Part 1 in an h3")

    buttons = section.find_all("button")
    if len(buttons) < 3:
        raise check50.Failure(
            f"expected at least three buttons in Part 1, but found {len(buttons)}"
        )


@check50.check(exists)
def free_response():
    """Part 2 has a question in an h3, an input field and a button"""
    section = part("Part 2")

    if section.find("h3") is None:
        raise check50.Failure("expected the question of Part 2 in an h3")

    if section.find("input") is None:
        raise check50.Failure("expected an input field in Part 2")

    if section.find("button") is None:
        raise check50.Failure("expected a button to confirm the answer in Part 2")


@check50.check(exists)
def javascript():
    """reacts to clicks with JavaScript"""
    code = "\n".join(script.get_text() for script in page().find_all("script"))
    handlers = page().find_all(attrs={"onclick": True})

    if (
        not re.search(r"addEventListener\s*\(\s*['\"]click['\"]|\.onclick\s*=", code)
        and not handlers
    ):
        raise check50.Failure(
            "expected JavaScript that reacts to clicks, e.g. with addEventListener('click', …)"
        )


@check50.check(javascript)
def feedback():
    '''answers with "Richtig!" and "Falsch!"'''
    text = html()

    for word in ("Richtig!", "Falsch!"):
        if word not in text:
            raise check50.Failure(f'expected the feedback "{word}" in index.html')


def html():
    """The text of index.html."""
    with open("index.html", encoding="utf-8") as file:
        return file.read()


def page():
    """index.html, parsed."""
    return BeautifulSoup(html(), "html.parser")


def part(title):
    """The element around the heading *title* ("Part 1"), as in the distribution code."""
    heading = page().find(["h2", "h3"], string=re.compile(re.escape(title)))
    if heading is None:
        raise check50.Failure(f'expected the heading "{title}" from the distribution code')

    return heading.parent
