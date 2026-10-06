import json
import re

import check50
import check50.flask
import check50.py


@check50.check()
def exists():
    """app.py and templates/index.html exist"""
    check50.exists("app.py", "templates/index.html")


@check50.check(exists)
def compiles():
    """app.py compiles"""
    check50.py.compile("app.py")


@check50.check(compiles)
def startup():
    """the app starts up"""
    check50.flask.app("app.py").get("/").status(200)


@check50.check(startup)
def form():
    """/ shows a form for name, month and day that sends by POST to /"""
    fields(check50.flask.app("app.py"))


@check50.check(form)
def adds():
    """adding a birthday redirects to /"""
    app = check50.flask.app("app.py")
    app.post("/", data=entry(app, "Harry", 7, 31), follow_redirects=False)

    status = app.status()
    location = app.response.headers.get("Location", "")

    if status not in (301, 302, 303, 307, 308) or not re.fullmatch(r"(https?://[^/]+)?/", location):
        raise check50.Failure(f"expected a redirect to /, but the app answered {status}")


@check50.check(adds)
def shows():
    """/ shows the birthday as a row of the table"""
    expect_rows(check50.flask.app("app.py"), [("Harry", 7, 31)])


@check50.check(shows)
def saves():
    """the birthday is saved in birthdays.json"""
    try:
        with open("birthdays.json") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise check50.Failure("expected birthdays.json, but it is missing") from None
    except ValueError as error:
        raise check50.Failure(f"expected birthdays.json to be valid JSON: {error}") from error

    if "Harry" not in json.dumps(data):
        raise check50.Failure("expected Harry in birthdays.json")


@check50.check(shows)
def several():
    """adds a second birthday below the first, each once"""
    app = check50.flask.app("app.py")
    app.post("/", data=entry(app, "Ron", 3, 1))

    expect_rows(check50.flask.app("app.py"), [("Harry", 7, 31), ("Ron", 3, 1)])


def fields(app):
    """The names of the form's fields for name, month and day, found on /."""
    page = app.get("/").status(200).content()
    forms = [found for found in page.find_all("form") if found.get("method", "").lower() == "post"]

    if not forms:
        raise check50.Failure('expected a form with method="post"')

    if forms[0].get("action", "/") not in ("/", ""):
        raise check50.Failure(f"expected the form to send to /, not {forms[0].get('action')}")

    names = [
        field.get("name")
        for field in forms[0].find_all(["input", "select"])
        if field.get("name") and field.get("type", "").lower() not in ("submit", "button", "hidden")
    ]

    found = {}

    for key, words in [("month", ("month", "monat")), ("day", ("day", "tag")), ("name", ("name",))]:
        matches = [
            name
            for name in names
            if any(word in name.lower() for word in words) and name not in found.values()
        ]

        if not matches:
            raise check50.Failure(f"expected a field for the {key} in the form, but found {names}")

        found[key] = matches[0]

    return found


def entry(app, name, month, day):
    """The form data for a birthday, under the form's own field names."""
    found = fields(app)

    return {found["name"]: name, found["month"]: str(month), found["day"]: str(day)}


def expect_rows(app, birthdays):
    """Expects one table row for each of *birthdays* on /, in order, and no other row for them."""
    page = app.get("/").status(200).content()
    rows = [" ".join(row.get_text(" ").split()) for row in page.find_all("tr")]
    positions = []

    for name, month, day in birthdays:
        matches = [
            index
            for index, text in enumerate(rows)
            if name in text and re.search(rf"\b{month}\b\D+\b{day}\b|\b{day}\b\D+\b{month}\b", text)
        ]

        if not matches:
            raise check50.Failure(f"expected a row with {name} and {month}/{day}, but found {rows}")

        if len(matches) > 1:
            raise check50.Failure(f"expected {name} once, but found {len(matches)} rows")

        positions.append(matches[0])

    if positions != sorted(positions):
        raise check50.Failure(
            f"expected the birthdays in the order they were added, but found {rows}"
        )
