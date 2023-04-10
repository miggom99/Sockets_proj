#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pytest

from server import (guess_is_correct, guess_client, find_client_id)

#dicionario usado para fazer os testes
#gamers = {"Manel": {"socket": "abc", "guess": 60, "max_attempts": 20, "attempts": 0, "cipher": 00000000}}
# a partir deste testes virifica-se as tres funcoes
def test():
	assert find_client_id("abc") == "Manel" 
	assert guess_client("abc", {"op": "GUESS", "number": 50, "cipher": None}) == { "op": "GUESS", "status":True, "result": "smaller" }
	assert guess_client("abc", {"op": "GUESS", "number": 80, "cipher": None}) == { "op": "GUESS", "status":True, "result": "larger" }
	assert guess_client("abc", {"op": "GUESS", "number": 60 ,"cipher": None}) == { "op": "GUESS", "status":True, "result": "equals" }
	assert guess_client("abcdef", {"op": "GUESS", "number": 60, "cipher": None}) == { "op": "GUESS", "status":False, "error": "Cliente inexistente" }
	assert guess_client("abc", {"op": "GUESS", "number": 105, "cipher": None}) == { "op": "GUESS", "status":False, 'error': 'Valor fora dos limites (0 <= number <= 100)'}
	

