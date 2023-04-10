#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pytest

from server import (stop_client, gamers, guess_client)
from client import stop_action

#é possivel testar o funcionamento do stop_action e do stop_client
#retirou-se clean_client(client_sock) da função stop_client porque compromete a realização da simulação
#se o não fize-se o jogador manel desaparecia do dicionario gamers, assim dava erro nos restantes testes
#o que comprova a eficacia da limpeza do dicionario, ou seja, da função clean_client
#gamers = {"Manel": {"socket": "abc", "guess": 60, "max_attempts": 20, "attempts": 20, "cipher": 00000000}}
#para testar as mensagens do stop_action teve-se de tirar client_sock.close () pois o socket de simulação não existe
#teve-se tambem de retirar sys.exit(0) se não a simulação seria abandonada meio
#os prints foram tambem trocados para returns

def test():
	assert stop_client("abc", {"op": "STOP", "number": 60, "attempts": 20}) == { "op": "STOP", "status":True, "guess": 60} 
	assert stop_action("abc", 20) == ("--- Parabéns!!! Terminou o jogo em 20 tentativas ---")
	assert stop_client("abcdef", {"op": "STOP", "number": 32, "attempts": 20}) == { "op": "STOP", "status":False, "error": "Cliente inexistente" }
	assert stop_client("abc", {"op": "STOP", "number": 60, "attempts": 8}) == { "op": "STOP", "status":False, "error": "Numero de jogadas inconsistente" }
	increment = guess_client("abc", {"op": "GUESS", "number": 50}) #para incrementar a contagem, para ser possivel realizar a proxima testagem
	assert stop_client("abc", {"op": "STOP", "number": 60, "attempts": 21}) == { "op": "STOP", "status":False, "error": "Excedeu o numero maximo de tentativas" }
	
