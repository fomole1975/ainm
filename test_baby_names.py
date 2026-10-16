import random

import pytest

from baby_names import NamePredictor, load_names, DEFAULT_FILE


@pytest.fixture
def tiny():
    return NamePredictor(["anna", "anne", "annie"], order=2)


@pytest.fixture
def full():
    return NamePredictor(load_names(DEFAULT_FILE), order=2)


def test_load_names_skips_comments_blanks_and_junk(tmp_path):
    f = tmp_path / "names.txt"
    f.write_text("# a comment\nAoife\n\nCian\nnot a name 123\n", encoding="utf-8")
    assert load_names(f) == ["Aoife", "Cian"]


def test_load_names_falls_back_when_file_missing(tmp_path, capsys):
    names = load_names(tmp_path / "nope.txt")
    assert len(names) > 0
    assert "built-in" in capsys.readouterr().out


def test_predict_next_is_deterministic_when_only_one_option(tiny):
    assert tiny.predict_next("an") == [("n", 1.0)]


def test_predict_next_probabilities_sum_to_one(tiny):
    results = tiny.predict_next("ann", top=10)
    assert {letter for letter, _ in results} == {"a", "e", "i"}
    assert sum(p for _, p in results) == pytest.approx(1.0)


def test_predict_next_unseen_context_returns_empty(tiny):
    assert tiny.predict_next("zz") == []


def test_predict_next_backs_off_to_shorter_context():
    p = NamePredictor(["anna"], order=3)
    # "xan" was never seen as a 3-letter context, but "an" and "n" were.
    assert p.predict_next("xan") != []


def test_generated_names_respect_length_limits(full):
    random.seed(1)
    names = full.suggest(25, min_len=4, max_len=7)
    assert names
    assert all(4 <= len(n) <= 7 for n in names)


def test_suggestions_are_new_names(full):
    random.seed(2)
    for name in full.suggest(25):
        assert name.lower() not in full.names


def test_prefix_is_respected(full):
    random.seed(3)
    names = full.suggest(10, prefix="Ma")
    assert names
    assert all(n.startswith("Ma") for n in names)


def test_suggestions_are_unique_and_capitalised(full):
    random.seed(4)
    names = full.suggest(20)
    assert len(names) == len(set(names))
    assert all(n[0].isupper() and n[1:].islower() for n in names)
