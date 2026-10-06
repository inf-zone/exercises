import glob
import os
import re

import check50
from bs4 import BeautifulSoup

#: The tags every page has anyway, which the task does not count.
BASIC_TAGS = {"html", "head", "body", "title"}


@check50.check()
def exists():
    """index.html, styles.css and specification.txt exist"""
    check50.exists("index.html", "styles.css", "specification.txt")


@check50.check(exists)
def pages():
    """there are at least four HTML pages"""
    found = sorted(glob.glob("*.html"))

    if len(found) < 4:
        raise check50.Failure(
            f"expected at least four .html pages, but found {len(found)}: {', '.join(found)}"
        )


@check50.check(pages)
def links():
    """every page links to every other page"""
    found = sorted(glob.glob("*.html"))

    for name in found:
        targets = {os.path.normpath(link.split("#")[0].split("?")[0]) for link in hrefs(name)}
        missing = [other for other in found if other != name and other not in targets]

        if missing:
            raise check50.Failure(f"expected {name} to link to {', '.join(missing)}")


@check50.check(exists)
def stylesheet():
    """every page uses styles.css"""
    for name in sorted(glob.glob("*.html")):
        head = parse(name).find("head")
        sheets = (
            []
            if head is None
            else [
                link.get("href", "")
                for link in head.find_all("link")
                if "stylesheet" in [value.lower() for value in link.get("rel", [])]
            ]
        )

        if "styles.css" not in [os.path.normpath(sheet) for sheet in sheets]:
            raise check50.Failure(
                f"expected {name} to include styles.css in its head: "
                '<link href="styles.css" rel="stylesheet">'
            )


@check50.check(pages)
def tags():
    """the pages use at least ten different HTML tags besides html, head, body and title"""
    used = set()

    for name in glob.glob("*.html"):
        used |= {tag.name for tag in parse(name).find_all(True)}

    used -= BASIC_TAGS

    if len(used) < 10:
        raise check50.Failure(
            f"expected at least ten different tags, but found {len(used)}: "
            + ", ".join(sorted(used))
        )


@check50.check(exists)
def css():
    """styles.css has at least five selectors and five properties"""
    with open("styles.css", encoding="utf-8") as file:
        text = re.sub(r"/\*.*?\*/", "", file.read(), flags=re.S)

    # Rules inside @media and the like count too: take each selector before a block of declarations.
    selectors = {
        selector.strip()
        for match in re.finditer(r"([^{}]+)\{[^{}]*\}", text)
        for selector in match.group(1).split(",")
        if selector.strip() and not selector.strip().startswith("@")
    }
    properties = set(re.findall(r"([-a-zA-Z]+)\s*:[^;{}]+(?:;|\})", text))

    if len(selectors) < 5:
        raise check50.Failure(
            f"expected at least five different selectors, but found {len(selectors)}"
        )

    if len(properties) < 5:
        raise check50.Failure(
            f"expected at least five different properties, but found {len(properties)}"
        )


@check50.check(exists)
def javascript():
    """a page uses JavaScript"""
    for name in glob.glob("*.html"):
        if parse(name).find("script") is not None:
            return

    raise check50.Failure("expected a <script> in at least one page")


@check50.check(exists)
def specification():
    """specification.txt is not empty"""
    with open("specification.txt", encoding="utf-8") as file:
        text = file.read()

    if not text.strip():
        raise check50.Failure("expected the tags, properties and JavaScript in specification.txt")


def parse(name):
    """The page *name*, parsed."""
    with open(name, encoding="utf-8") as file:
        return BeautifulSoup(file.read(), "html.parser")


def hrefs(name):
    """The local links of the page *name*."""
    return [
        link.get("href", "")
        for link in parse(name).find_all("a")
        if link.get("href") and not re.match(r"[a-z]+:|//", link.get("href"))
    ]
