import re

import check50
import check50.flask
import check50.py

FILES = ["app.py", "templates/layout.html", "templates/index.html", "templates/color.html"]


@check50.check()
def exists():
    """app.py, templates/layout.html, templates/index.html, templates/color.html exist"""
    check50.exists(*FILES)


@check50.check(exists)
def compiles():
    """app.py compiles"""
    check50.py.compile("app.py")


@check50.check(compiles)
def startup():
    """the app starts up"""
    check50.flask.app("app.py").get("/").status(200)


@check50.check(startup)
def heading():
    """/ shows the heading "Hallo, Flask" from the layout"""
    check50.flask.app("app.py").get("/").status(200).content(
        r"Hallo,\s*Flask", "Hallo, Flask", name="h1"
    )


@check50.check(startup)
def form():
    """/ shows a form that sends red or blue as color by POST"""
    page = check50.flask.app("app.py").get("/").status(200).content()
    forms = [found for found in page.find_all("form") if found.get("method", "").lower() == "post"]

    if not forms:
        raise check50.Failure('expected a form with method="post"')

    select = forms[0].find(attrs={"name": "color"})

    if select is None:
        raise check50.Failure('expected a field with name="color" in the form')

    values = {option.get("value") for option in select.find_all("option")}

    for color in ("red", "blue"):
        if color not in values:
            raise check50.Failure(f'expected an option with value="{color}"')


@check50.check(form)
def red():
    """sending red shows "Ihre Lieblingsfarbe ist red." in red"""
    favourite("red")


@check50.check(form)
def blue():
    """sending blue shows "Ihre Lieblingsfarbe ist blue." in blue"""
    favourite("blue")


@check50.check(red)
def invalid():
    """does not accept another color"""
    app = check50.flask.app("app.py").post("/", data={"color": "green"})

    if app.status() >= 500:
        raise check50.Failure(
            f"expected the app to handle the color green, but it answered {app.status()}"
        )

    if re.search(r"Lieblingsfarbe ist\s*green", app.response.get_data(as_text=True)):
        raise check50.Failure(
            'expected the app to reject green, but it showed "Ihre Lieblingsfarbe ist green."'
        )


def favourite(color):
    """Sends *color* and expects the sentence in that color, inside the layout."""
    page = (
        check50.flask.app("app.py")
        .post("/", data={"color": color})
        .status(200)
        .content(rf"Ihre Lieblingsfarbe ist\s*{color}\.", f"Ihre Lieblingsfarbe ist {color}.")
        .content(r"Hallo,\s*Flask", "Hallo, Flask", name="h1")
        .content()
    )

    sentence = page.find(string=re.compile(rf"Lieblingsfarbe ist\s*{color}"))
    styled = [
        element
        for element in [sentence.parent, *sentence.parent.parents]
        if re.search(rf"color\s*:\s*{color}\b", element.get("style", "") or "")
    ]

    if not styled:
        raise check50.Failure(f'expected the sentence in an element with style="color: {color}"')
