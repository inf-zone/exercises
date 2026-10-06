import datetime
import sys
import types

import check50
import check50.py

FILE = "mastodon_oop.py"
UTC = datetime.UTC


@check50.check()
def exists():
    """mastodon_oop.py exists"""
    check50.exists(FILE)


@check50.check(exists)
def imports():
    """mastodon_oop.py can be imported"""
    load_module()


@check50.check(imports)
def inheritance():
    """each trigger inherits from its superclass"""
    module = load_module()
    for name, superclass in [
        ("MediaTrigger", "Trigger"),
        ("ImageMediaTrigger", "MediaTrigger"),
        ("VideoMediaTrigger", "MediaTrigger"),
        ("PhraseTrigger", "Trigger"),
        ("TimeTrigger", "Trigger"),
        ("BeforeTrigger", "TimeTrigger"),
        ("AfterTrigger", "TimeTrigger"),
        ("NotTrigger", "Trigger"),
        ("AndTrigger", "Trigger"),
        ("OrTrigger", "Trigger"),
    ]:
        cls = getattr(module, name, None)

        if not isinstance(cls, type):
            raise check50.Failure(f"expected a class {name}")

        if not issubclass(cls, getattr(module, superclass)):
            raise check50.Failure(f"expected {name} to inherit from {superclass}")


@check50.check(imports)
def media_trigger():
    """MediaTrigger fires for a toot with media"""
    module = load_module()
    trigger = make(module, "MediaTrigger")

    expect(trigger, "MediaTrigger()", TOOT_A, False)
    expect(trigger, "MediaTrigger()", TOOT_B, True)
    expect(trigger, "MediaTrigger()", TOOT_VIDEO, True)


@check50.check(imports)
def image_trigger():
    """ImageMediaTrigger fires only for a toot with an image"""
    module = load_module()
    trigger = make(module, "ImageMediaTrigger")

    expect(trigger, "ImageMediaTrigger()", TOOT_A, False)
    expect(trigger, "ImageMediaTrigger()", TOOT_B, True)
    expect(trigger, "ImageMediaTrigger()", TOOT_VIDEO, False)


@check50.check(imports)
def video_trigger():
    """VideoMediaTrigger fires only for a toot with a video"""
    module = load_module()
    trigger = make(module, "VideoMediaTrigger")

    expect(trigger, "VideoMediaTrigger()", TOOT_A, False)
    expect(trigger, "VideoMediaTrigger()", TOOT_B, False)
    expect(trigger, "VideoMediaTrigger()", TOOT_VIDEO, True)


@check50.check(imports)
def phrase_trigger():
    """PhraseTrigger fires for a phrase in the text, ignoring case"""
    module = load_module()

    expect(make(module, "PhraseTrigger", "Python"), 'PhraseTrigger("Python")', TOOT_A, True)
    expect(make(module, "PhraseTrigger", "python"), 'PhraseTrigger("python")', TOOT_A, True)
    expect(make(module, "PhraseTrigger", "PYTHON"), 'PhraseTrigger("PYTHON")', TOOT_A, True)
    expect(make(module, "PhraseTrigger", "Java"), 'PhraseTrigger("Java")', TOOT_A, False)
    expect(make(module, "PhraseTrigger", "lerne ich"), 'PhraseTrigger("lerne ich")', TOOT_A, True)


@check50.check(phrase_trigger)
def phrase_punctuation():
    """PhraseTrigger ignores . , ! and ? in the text"""
    module = load_module()
    toot = Toot("Erst Python, dann Flask. Oder?", [], A_TIME)

    expect(
        make(module, "PhraseTrigger", "python dann flask oder"),
        'PhraseTrigger("python dann flask oder")',
        toot,
        True,
    )


@check50.check(imports)
def before_trigger():
    """BeforeTrigger fires for a toot before the time, in EST by default"""
    module = load_module()

    # 8:00 EST is 13:00 UTC: toot A is from 12:00 UTC, toot B from 14:00 UTC.
    trigger = make(module, "BeforeTrigger", "2026-01-10 08:00:00")

    expect(trigger, 'BeforeTrigger("2026-01-10 08:00:00")', TOOT_A, True)
    expect(trigger, 'BeforeTrigger("2026-01-10 08:00:00")', TOOT_B, False)


@check50.check(imports)
def after_trigger():
    """AfterTrigger fires for a toot after the time, in EST by default"""
    module = load_module()
    trigger = make(module, "AfterTrigger", "2026-01-10 08:00:00")

    expect(trigger, 'AfterTrigger("2026-01-10 08:00:00")', TOOT_A, False)
    expect(trigger, 'AfterTrigger("2026-01-10 08:00:00")', TOOT_B, True)


@check50.check(before_trigger)
def time_zone():
    """time triggers take another time zone"""
    module = load_module()
    trigger = make(module, "BeforeTrigger", "2026-01-10 13:30:00", "UTC")

    expect(trigger, 'BeforeTrigger("2026-01-10 13:30:00", "UTC")', TOOT_A, True)
    expect(trigger, 'BeforeTrigger("2026-01-10 13:30:00", "UTC")', TOOT_B, False)

    trigger = make(module, "AfterTrigger", "2026-01-10 13:30:00", "Europe/Berlin")

    expect(trigger, 'AfterTrigger("2026-01-10 13:30:00", "Europe/Berlin")', TOOT_A, False)
    expect(trigger, 'AfterTrigger("2026-01-10 13:30:00", "Europe/Berlin")', TOOT_B, True)


@check50.check(after_trigger)
def strictly():
    """time triggers do not fire at exactly the time"""
    module = load_module()
    toot = Toot("Punkt eins", [], datetime.datetime(2026, 1, 10, 13, 0, tzinfo=UTC))

    expect(
        make(module, "BeforeTrigger", "2026-01-10 08:00:00"),
        'BeforeTrigger("2026-01-10 08:00:00")',
        toot,
        False,
    )
    expect(
        make(module, "AfterTrigger", "2026-01-10 08:00:00"),
        'AfterTrigger("2026-01-10 08:00:00")',
        toot,
        False,
    )


@check50.check(imports)
def not_trigger():
    """NotTrigger inverts a trigger"""
    module = load_module()

    expect(make(module, "NotTrigger", ALWAYS), "NotTrigger(always)", TOOT_A, False)
    expect(make(module, "NotTrigger", NEVER), "NotTrigger(never)", TOOT_A, True)


@check50.check(imports)
def and_trigger():
    """AndTrigger fires only if both triggers fire"""
    module = load_module()

    for first, second in [(ALWAYS, ALWAYS), (ALWAYS, NEVER), (NEVER, ALWAYS), (NEVER, NEVER)]:
        expect(
            make(module, "AndTrigger", first, second),
            f"AndTrigger({first}, {second})",
            TOOT_A,
            first.result and second.result,
        )


@check50.check(imports)
def or_trigger():
    """OrTrigger fires if at least one trigger fires"""
    module = load_module()

    for first, second in [(ALWAYS, ALWAYS), (ALWAYS, NEVER), (NEVER, ALWAYS), (NEVER, NEVER)]:
        expect(
            make(module, "OrTrigger", first, second),
            f"OrTrigger({first}, {second})",
            TOOT_A,
            first.result or second.result,
        )


@check50.check(imports)
def filters():
    """filter_toots keeps the toots every trigger fires for"""
    module = load_module()
    toots = [TOOT_A, TOOT_B, TOOT_VIDEO]
    image = make(module, "ImageMediaTrigger")
    python = make(module, "PhraseTrigger", "python")

    for triggers, shown, expected in [
        ([python], '[PhraseTrigger("python")]', [TOOT_A, TOOT_B]),
        ([python, image], '[PhraseTrigger("python"), ImageMediaTrigger()]', [TOOT_B]),
        ([NEVER], "[never]", []),
        ([], "[]", toots),
    ]:
        try:
            actual = module.filter_toots(list(toots), triggers)
        except Exception as error:
            raise check50.Failure(f"filter_toots raised {type(error).__name__}: {error}") from error

        if not isinstance(actual, list) or actual != expected:
            raise check50.Failure(
                f"expected filter_toots with {shown} to keep {names(expected)}, "
                f"not {names(actual) if isinstance(actual, list) else repr(actual)}"
            )


@check50.check(and_trigger)
def example():
    """the example from the task: mentions Python and has no image"""
    module = load_module()
    trigger = make(
        module,
        "AndTrigger",
        make(module, "PhraseTrigger", "python"),
        make(module, "NotTrigger", make(module, "ImageMediaTrigger")),
    )
    shown = 'AndTrigger(PhraseTrigger("python"), NotTrigger(ImageMediaTrigger()))'

    expect(trigger, shown, TOOT_A, True)
    expect(trigger, shown, TOOT_B, False)


class Toot:
    """A toot as the triggers see it: content, media and pubdate, read-only."""

    def __init__(self, content, media, pubdate, name=None):
        self._content = content
        self._media = [Entity(item) for item in media]
        self._pubdate = pubdate
        self.name = name or repr(content)

    content = property(lambda self: self._content)
    media = property(lambda self: self._media)
    pubdate = property(lambda self: self._pubdate)
    account = property(lambda self: "alice")
    hashtags = property(lambda self: ["python"])

    def __repr__(self):
        return self.name


class Fixed:
    """A trigger that always gives *result*."""

    def __init__(self, result):
        self.result = result

    def evaluate(self, toot):
        return self.result

    def __str__(self):
        return "always" if self.result else "never"


class Entity(dict):
    """A dict whose keys are attributes too, as Mastodon.py returns them."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None


A_TIME = datetime.datetime(2026, 1, 10, 12, 0, tzinfo=UTC)
TOOT_A = Toot("Heute lerne ich Python!", [], A_TIME, "toot A")
TOOT_B = Toot(
    "Mein Python-Setup, siehe Foto.",
    [{"type": "image", "url": "https://example.org/foto.jpg"}],
    datetime.datetime(2026, 1, 10, 14, 0, tzinfo=UTC),
    "toot B",
)
TOOT_VIDEO = Toot(
    "Ein Video ohne Worte",
    [
        {"type": "gifv", "url": "https://example.org/a.gif"},
        {"type": "video", "url": "https://example.org/b.mp4"},
    ],
    datetime.datetime(2026, 1, 11, 9, 0, tzinfo=UTC),
    "a toot with a video",
)
ALWAYS = Fixed(True)
NEVER = Fixed(False)


def names(toots):
    """*toots* as the messages name them."""
    return "[" + ", ".join(repr(toot) for toot in toots) + "]"


def make(module, name, *args):
    """A trigger of *module*'s class *name*, made with *args*."""
    cls = getattr(module, name, None)

    if cls is None:
        raise check50.Failure(f"expected a class {name}")

    try:
        return cls(*args)
    except Exception as error:
        shown = ", ".join(f'"{arg}"' if isinstance(arg, str) else str(arg) for arg in args)
        raise check50.Failure(f"{name}({shown}) raised {type(error).__name__}: {error}") from error


def expect(trigger, shown, toot, expected):
    """Evaluates *trigger* for *toot* and expects *expected*."""
    try:
        actual = trigger.evaluate(toot)
    except Exception as error:
        raise check50.Failure(
            f"{shown}.evaluate({toot!r}) raised {type(error).__name__}: {error}"
        ) from error

    if bool(actual) != expected:
        raise check50.Failure(f"expected {shown} to give {expected} for {toot!r}, not {actual!r}")


def load_module():
    """mastodon_oop.py, imported with a stand-in for Mastodon.py, which has no network here."""

    class Mastodon:
        def __init__(self, *args, **kwargs):
            pass

        def timeline_hashtag(self, *args, **kwargs):
            return []

    stand_in = types.ModuleType("mastodon")
    stand_in.Mastodon = Mastodon
    # Any other name, such as an exception class, is an empty class.
    stand_in.__getattr__ = lambda name: type(name, (Exception,), {})
    sys.modules["mastodon"] = stand_in

    try:
        return check50.py.import_(FILE)
    except check50.Failure:
        raise
    except BaseException as error:
        raise check50.Failure(f"importing {FILE} raised {type(error).__name__}: {error}") from error
