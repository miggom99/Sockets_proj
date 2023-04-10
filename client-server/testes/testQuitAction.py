import pytest

from client import quit_action


def test():
	assert quit_action("abcd", 3) == "--- Desistiu com sucesso ---"
	assert quit_action("dfghb", 7) == "--- Desistiu com sucesso ---"
