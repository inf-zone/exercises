import check50
import check50.c


@check50.check()
def exists():
    """scrabble.c exists"""
    check50.exists("scrabble.c")


@check50.check(exists)
def compiles():
    """scrabble.c compiles"""
    check50.c.compile("scrabble.c", lcs50=True)


@check50.check(compiles)
def uppercase_wins():
    """identifies 'LETTERCASE' as winner over 'lettercase'"""
    winner("LETTERCASE", "lettercase", 1)


@check50.check(compiles)
def uppercase_wins_second():
    """identifies 'DOG' as winner over 'dog'"""
    winner("dog", "DOG", 2)


@check50.check(compiles)
def mixed_case_tie():
    """identifies 'Aa' and 'aaa' as a tie"""
    tie("Aa", "aaa")


@check50.check(compiles)
def doubled_beats_more_letters():
    """identifies 'ZOO' as winner over 'quiz'"""
    winner("ZOO", "quiz", 1)


@check50.check(compiles)
def punctuation_still_zero():
    """still identifies 'Question?' and 'Question!' as a tie"""
    tie("Question?", "Question!")


@check50.check(compiles)
def lowercase_unchanged():
    """still identifies 'pig' as winner over 'dog'"""
    winner("pig", "dog", 1)


def winner(word1, word2, player):
    check50.run("./scrabble").stdin(word1).stdin(word2).stdout(
        f"[Pp]layer {player} [Ww]ins!?", f"Player {player} wins!"
    ).exit(0)


def tie(word1, word2):
    check50.run("./scrabble").stdin(word1).stdin(word2).stdout("[Tt]ie!?", "Tie!").exit(0)
