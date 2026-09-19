# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from pathlib import Path

from vial_culex import QUESTION

REPO = Path(__file__).resolve().parents[1]


def test_readme() -> None:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert text.startswith("# vial_culex\n")
    body = text.split("\n", 1)[1].lstrip()
    assert body.startswith(QUESTION)
    assert "What it is not" not in text
    assert "—" not in text
    assert "z_max=3.0" in text
    assert "fa819c7" in text
    assert "0 of 3" in text
    assert "blank founders" in text
    assert "69f4f6d" in text
    assert "hand-off" in text
    assert "M0=200" in text or "m0=200" in text
    assert ".venv/bin/python -m pytest" in text
    assert "12835f747d6360781f3cc7f91f243178" in text
    assert "[Fly research index](" in text
    agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
    long_arm = (REPO / "LONG_ARM.md").read_text(encoding="utf-8")
    assert "—" not in agents
    assert "—" not in long_arm
    assert "Do not pin GraphForge" in agents
    assert "p_thief" in agents
    assert (REPO / "LICENSE").is_file()


def test_methods_card_and_citation() -> None:
    methods = (REPO / "METHODS.yaml").read_text(encoding="utf-8")
    assert "science_lock:" in methods
    assert "pre_specified: false" in methods
    assert "—" not in methods
    assert "What it is not" not in methods
    cite = (REPO / "CITATION.cff").read_text(encoding="utf-8")
    assert "cff-version: 1.2.0" in cite
    assert "Martial Systems LLC" in cite
