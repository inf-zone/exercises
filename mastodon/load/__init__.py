import datetime
import sys
import types

import check50
import check50.py

FILE = "mastodon_oop.py"
UTC = datetime.UTC

#: Status dicts as Mastodon.py returns them, cut down to what the task uses.
STATUSES = [
    {
        "content": (
            '<p>Heute lerne ich <a href="https://mastodon.social/tags/python" '
            'class="mention hashtag" rel="tag">#<span>Python</span></a>!</p>'
        ),
        "account": {"acct": "alice", "display_name": "Alice"},
        "tags": [{"name": "python", "url": "https://mastodon.social/tags/python"}],
        "created_at": datetime.datetime(2026, 1, 10, 12, 0, tzinfo=UTC),
        "media_attachments": [],
    },
    {
        "content": "<p>Mein Python-Setup, siehe <strong>Foto</strong>.</p>",
        "account": {"acct": "bob@example.org", "display_name": "Bob"},
        "tags": [{"name": "python", "url": ""}, {"name": "setup", "url": ""}],
        "created_at": datetime.datetime(2026, 1, 10, 14, 0, tzinfo=UTC),
        "media_attachments": [{"type": "image", "url": "https://example.org/foto.jpg"}],
    },
    {
        "content": "<p>Ohne Hashtags</p>",
        "account": {"acct": "carol", "display_name": "Carol"},
        "tags": [],
        "created_at": datetime.datetime(2026, 1, 11, 9, 30, tzinfo=UTC),
        "media_attachments": [],
    },
]


@check50.check()
def exists():
    """mastodon_oop.py exists"""
    check50.exists(FILE)


@check50.check(exists)
def imports():
    """mastodon_oop.py can be imported"""
    load_module()


@check50.check(imports)
def toot_properties():
    """Toot makes its five parameters readable as properties"""
    module = load_module()
    pubdate = datetime.datetime(2026, 1, 10, 12, 0, tzinfo=UTC)
    toot = make_toot(module, "Hallo", "alice", ["python"], pubdate, [])

    for name, expected in [
        ("content", "Hallo"),
        ("account", "alice"),
        ("hashtags", ["python"]),
        ("pubdate", pubdate),
        ("media", []),
    ]:
        if not isinstance(getattr(module.Toot, name, None), property):
            raise check50.Failure(f"expected Toot.{name} to be a @property")

        actual = getattr(toot, name)

        if actual != expected:
            raise check50.Failure(f"expected toot.{name} to be {expected!r}, not {actual!r}")


@check50.check(imports)
def toot_str():
    """str of a Toot shows its account and content"""
    module = load_module()
    toot = make_toot(
        module,
        "Mein Python-Setup",
        "bob",
        ["python"],
        datetime.datetime(2026, 1, 10, 14, 0, tzinfo=UTC),
        [],
    )

    try:
        text = str(toot)
    except Exception as error:
        raise check50.Failure(f"str(toot) raised {type(error).__name__}: {error}") from error

    for part in ("bob", "Mein Python-Setup"):
        if part not in text:
            raise check50.Failure(
                f'expected str(toot) to contain "{part}", but it returned {text!r}'
            )


@check50.check(imports)
def text_content():
    """get_text_content returns the text of a toot without HTML"""
    module = load_module()

    try:
        text = module.get_text_content(entity(STATUSES[0]))
    except Exception as error:
        raise check50.Failure(f"get_text_content raised {type(error).__name__}: {error}") from error

    if not isinstance(text, str) or text.strip() != "Heute lerne ich #Python!":
        raise check50.Mismatch("Heute lerne ich #Python!", repr(text))


@check50.check(imports)
def loads():
    """load asks Mastodon for 10 toots with the hashtag"""
    module = load_module()
    calls = module.mastodon_calls
    call_load(module, "python")

    if not calls:
        raise check50.Failure("expected load to call mastodon.timeline_hashtag, but it did not")

    hashtag, args, kwargs = calls[0]

    if hashtag != "python":
        raise check50.Failure(f'expected the hashtag "python", not {hashtag!r}')

    if kwargs.get("limit", args[4] if len(args) > 4 else None) != 10:
        raise check50.Failure("expected timeline_hashtag to be called with limit=10")


@check50.check(loads)
def load_toots():
    """load returns a Toot for each status"""
    module = load_module()
    toots = call_load(module, "python")

    if not isinstance(toots, list):
        raise check50.Failure(f"expected load to return a list, not {type(toots).__name__}")

    if len(toots) != len(STATUSES):
        raise check50.Failure(f"expected {len(STATUSES)} toots, not {len(toots)}")

    for toot in toots:
        if not isinstance(toot, module.Toot):
            raise check50.Failure(
                f"expected a list of Toot objects, but found {type(toot).__name__}"
            )


@check50.check(load_toots)
def load_fields():
    """load fills content, account, hashtags, pubdate and media"""
    module = load_module()
    toots = call_load(module, "python")

    expected = [
        ("Heute lerne ich #Python!", "alice", ["python"], STATUSES[0]["created_at"], 0),
        (
            "Mein Python-Setup, siehe Foto.",
            "bob@example.org",
            ["python", "setup"],
            STATUSES[1]["created_at"],
            1,
        ),
        ("Ohne Hashtags", "carol", [], STATUSES[2]["created_at"], 0),
    ]

    for toot, (content, account, hashtags, pubdate, media) in zip(toots, expected, strict=True):
        if not isinstance(toot.content, str) or toot.content.strip() != content:
            raise check50.Failure(f"expected the content {content!r}, not {toot.content!r}")

        if toot.account != account:
            raise check50.Failure(
                f'expected the account {account!r} (its "acct"), not {toot.account!r}'
            )

        if list(toot.hashtags) != hashtags:
            raise check50.Failure(f"expected the hashtags {hashtags!r}, not {toot.hashtags!r}")

        if toot.pubdate != pubdate:
            raise check50.Failure(
                f'expected the pubdate {pubdate} (the "created_at"), not {toot.pubdate!r}'
            )

        if len(toot.media) != media:
            raise check50.Failure(f"expected {media} media attachments, not {len(toot.media)}")


def load_module():
    """mastodon_oop.py, imported with a stand-in for Mastodon.py, which has no network here."""
    calls = []

    class Mastodon:
        def __init__(self, *args, **kwargs):
            pass

        def timeline_hashtag(self, hashtag, *args, **kwargs):
            calls.append((hashtag, args, kwargs))
            return [entity(status) for status in STATUSES]

    stand_in = types.ModuleType("mastodon")
    stand_in.Mastodon = Mastodon
    # Any other name, such as an exception class, is an empty class.
    stand_in.__getattr__ = lambda name: type(name, (Exception,), {})
    sys.modules["mastodon"] = stand_in

    try:
        module = check50.py.import_(FILE)
    except check50.Failure:
        raise
    except BaseException as error:
        raise check50.Failure(f"importing {FILE} raised {type(error).__name__}: {error}") from error

    module.mastodon_calls = calls

    return module


def call_load(module, hashtag):
    """*module*'s load(*hashtag*), with any error as a failure."""
    try:
        return module.load(hashtag)
    except Exception as error:
        raise check50.Failure(f"load raised {type(error).__name__}: {error}") from error


def make_toot(module, *args):
    """A Toot of *module* made with *args*, with any error as a failure."""
    try:
        return module.Toot(*args)
    except Exception as error:
        raise check50.Failure(
            "Toot(content, account, hashtags, pubdate, media) raised "
            f"{type(error).__name__}: {error}"
        ) from error


class Entity(dict):
    """A dict whose keys are attributes too, as Mastodon.py returns them."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None


def entity(value):
    """*value* with every dict in it an :class:`Entity`."""
    if isinstance(value, dict):
        return Entity({key: entity(item) for key, item in value.items()})
    if isinstance(value, list):
        return [entity(item) for item in value]
    return value
