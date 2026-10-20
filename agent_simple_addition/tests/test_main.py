import pytest

from src.main import add, main


def test_adds_two_numbers() -> None:
    """Verify that add returns the sum of two numbers."""
    assert add(2.5, 3.5) == 6.0


def test_adds_negative_numbers() -> None:
    """Verify that add handles negative operands."""
    assert add(-2.0, 5.0) == 3.0


def test_main_reads_numbers_and_prints_sum(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify that main reads two numbers and prints their sum."""
    inputs = iter(("2", "3"))
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main()

    assert capsys.readouterr().out == "5.0\n"