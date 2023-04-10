#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pytest

from server import (update_file, find_client_id, new_client, quit_client, gamers, clean_client)
#chamo update_file porque está dentro do quit_client

#dicionario usado para fazer os testes
#gamers = {"Manel": {"socket": "abc", "guess": 60, "max_attempts": 20, "attempts": 0, "cipher": 00000000}}
# a partir deste testes virifica-se as tres funcoes

def test():
	assert new_client("abc", {"op": "START", "client_id": "Manel", "cipher": None}) == { "op": "START", "status":False, "error": "cliente existente" }
	assert new_client("abcd", {"op": "START", "client_id": "Paula", "cipher": None}) == { "op": "START", "status":True, "max_attempts": gamers["Paula"]["max_attempts"] }
	assert quit_client("abcd", {"op": "QUIT"}) == { "op": "QUIT", "status":True}
	assert quit_client("abcde", {"op": "QUIT"}) == { "op": "QUIT", "status":False, "error": "cliente inxistente" }
	assert clean_client("abc") == True
	assert clean_client("4515") == False
	##achas que faz sentido meter mais?
