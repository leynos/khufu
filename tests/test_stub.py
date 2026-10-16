"""Tests for the generated package stub."""

from __future__ import annotations

import khufu


def test_hello_returns_stub_greeting() -> None:
    """The generated package exposes a working greeting."""
    assert khufu.hello() == "hello from Python"
