#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pytest

from client import validate_response

#Teste  para cada caso que a função validate_response pode ter

def test():
	assert validate_response("abc", { "op": "STOP", "status":False, "error": "Cliente inexistente" }) == "--- Erro: " + "Cliente inexistente" + " ---"
	assert validate_response("abcs", { "op": "STOP", "status":False, "error": "Excedeu o numero maximo de tentativas" })  == "--- Erro: " + "Excedeu o numero maximo de tentativas" + " ---"
	assert validate_response("avdsefg", { "op": "STOP", "status":False, "error": "Numero de jogadas inconsistente" }) == "--- Erro: " + "Numero de jogadas inconsistente" + " ---"
	assert validate_response("ghjkl", {"op":"Sair", "status": False, "error": "Operação inexistente (operações possivesis: \"START\", \"GUESS\", \"QUIT\", \"STOP\")"}) == "--- Erro: " + "Operação inexistente (operações possivesis: \"START\", \"GUESS\", \"QUIT\", \"STOP\")" + " ---"
	assert validate_response("1234",  {"op": "GUESS", "status":False, "error": "Tem de inserir um valor do tipo inteiro positivo" })	== "--- Erro: " + "Tem de inserir um valor do tipo inteiro positivo" + " ---"
	assert validate_response("aghsj", { "op": "GUESS", "status":False, "error": "Valor fora dos limites (0 <= number <= 100)" }) == "--- Erro: " + "Valor fora dos limites (0 <= number <= 100)" + " ---"
	assert validate_response("dscfew", { "op": "START", "status":True, "max_attempts": 22 }) == True
	assert validate_response("sgdhensm", { "op": "QUIT", "status":True}) == True
	assert validate_response("fdfwd", { "op": "GUESS", "status":True, "result": 20 }) == True
