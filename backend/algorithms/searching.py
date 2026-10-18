"""Shared validated input for integer searches."""

from backend.algorithms.sorting import IntegerArrayInput, SafeInteger


class SearchInput(IntegerArrayInput):
    target: SafeInteger
