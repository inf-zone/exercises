import check50
import check50.flask
import check50.py

USER = ("_cs50", "ohHai28!")


@check50.check()
def exists():
    """app.py and helpers.py exist"""
    check50.exists("app.py", "helpers.py")
    check50.include("lookup.py")
    check50.py.append_code("helpers.py", "lookup.py")


@check50.check(exists)
def compiles():
    """app.py compiles"""
    check50.py.compile("app.py")


@check50.check(compiles)
def templates():
    """the templates of the distribution code exist"""
    check50.exists(
        *(f"templates/{name}.html" for name in ("layout", "login", "register", "apology"))
    )


@check50.check(templates)
def startup():
    """the app starts up"""
    Finance().get("/").status(200)


@check50.check(startup)
def register():
    """registering a user succeeds and shows the portfolio"""
    Finance().register(*USER).status(200)


@check50.check(register)
def quote_page():
    """quote page has a form with a field symbol"""
    Finance().login(*USER).validate_form("/quote", ["symbol"])


@check50.check(quote_page)
def quote_invalid():
    """quote apologizes for an invalid symbol"""
    Finance().login(*USER).quote("ZZZZ").apology()


@check50.check(quote_page)
def quote_blank():
    """quote apologizes for a blank symbol"""
    Finance().login(*USER).quote("").apology()


@check50.check(quote_page)
def quote_valid():
    """quote shows the price of a valid symbol"""
    Finance().login(*USER).quote("AAAA").status(200).content(r"28\.00", "28.00", name="body")


@check50.check(register)
def buy_page():
    """buy page has a form with fields symbol and shares"""
    Finance().login(*USER).validate_form("/buy", ["symbol", "shares"])


@check50.check(buy_page)
def buy_invalid():
    """buy apologizes for an invalid symbol"""
    Finance().login(*USER).transaction("/buy", "ZZZZ", "2").apology()


@check50.check(buy_page)
def buy_shares():
    """buy apologizes for fractional, negative and non-numeric shares"""
    finance = Finance().login(*USER)

    for shares in ("-1", "0", "1.5", "foo"):
        finance.transaction("/buy", "AAAA", shares).apology(f"buying {shares} shares")


@check50.check(buy_page)
def buy_unaffordable():
    """buy apologizes if the user cannot afford the shares"""
    Finance().login(*USER).transaction("/buy", "CCCC", "6").apology("buying shares for $12,000.00")


@check50.check(buy_page)
def buy_valid():
    """buy buys shares and redirects to the portfolio"""
    (
        Finance()
        .login(*USER)
        .transaction("/buy", "AAAA", "1")
        .status(200)
        .transaction("/buy", "AAAA", "3")
        .status(200)
    )


@check50.check(buy_valid)
def index():
    """the portfolio shows the shares, their value, the cash and the total"""
    (
        Finance()
        .login(*USER)
        .get("/")
        .status(200)
        .content("AAAA")
        .content(r"112\.00", "112.00 (4 shares of AAAA at $28.00)")
        .content(r"9,?888\.00", "9,888.00 (the cash left)")
        .content(r"10,?000\.00", "10,000.00 (cash and shares)")
    )


@check50.check(buy_valid)
def sell_page():
    """sell page has a form with a select symbol and a field shares"""
    (
        Finance()
        .login(*USER)
        .validate_form("/sell", ["shares"])
        .validate_form("/sell", ["symbol"], field_tag="select")
    )


@check50.check(sell_page)
def sell_invalid():
    """sell apologizes for more shares than the user owns"""
    Finance().login(*USER).transaction("/sell", "AAAA", "8").apology("selling 8 of 4 shares")


@check50.check(sell_page)
def sell_valid():
    """sell sells shares and credits the cash"""
    (
        Finance()
        .login(*USER)
        .transaction("/sell", "AAAA", "2")
        .status(200)
        .get("/")
        .content(r"56\.00", "56.00 (2 shares of AAAA at $28.00)")
        .content(r"9,?944\.00", "9,944.00 (the cash after selling)")
    )


@check50.check(sell_valid)
def history():
    """history shows every purchase and sale"""
    page = Finance().login(*USER).get("/history").status(200).content(r"28\.00", "28.00").content()
    rows = [row for row in page.find_all("tr") if "AAAA" in row.get_text()]

    if len(rows) < 3:
        raise check50.Failure(
            f"expected a row for each of 3 transactions of AAAA, but found {len(rows)}"
        )


class Finance(check50.flask.app):
    """The app, with the requests the checks send."""

    def __init__(self):
        super().__init__("app.py")

    def register(self, username, password):
        return self.post(
            "/register", data={"username": username, "password": password, "confirmation": password}
        )

    def login(self, username, password):
        return self.post("/login", data={"username": username, "password": password})

    def quote(self, symbol):
        return self.post("/quote", data={"symbol": symbol})

    def transaction(self, route, symbol, shares):
        return self.post(route, data={"symbol": symbol, "shares": shares})

    def apology(self, what=None):
        """Expects the last response to be an apology: a status from 400 to 499."""
        status = self.status()

        if not 400 <= status < 500:
            about = f" for {what}" if what else ""
            raise check50.Failure(
                f"expected an apology (status 400){about}, but the app answered {status}"
            )

        return self

    def validate_form(self, route, fields, field_tag="input"):
        """Expects a form on *route*: one *field_tag* per name in *fields*, and a submit button."""
        content = self.get(route).status(200).content()
        names = [tag.attrs.get("name") for tag in content.find_all(field_tag)]

        for field in fields:
            if names.count(field) == 0:
                raise check50.Failure(
                    f'expected a {field_tag} field with name "{field}", but none was found'
                )

            if names.count(field) > 1:
                raise check50.Failure(f'found more than one field called "{field}"')

        if (
            content.find("button", type="submit") is None
            and content.find("input", type="submit") is None
        ):
            raise check50.Failure("expected a button to submit the form, but none was found")

        return self
