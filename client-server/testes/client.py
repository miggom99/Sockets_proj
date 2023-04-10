#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import socket
import json
import base64
from common_comm import send_dict, recv_dict, sendrecv_dict

from Crypto.Cipher import AES

# Função para encriptar valores a enviar em formato jsos com codificação base64
# return int data encrypted in a 16 bytes binary string coded in base64
def encrypt_intvalue (cipherkey, number):
	if cipherkey == "Y" or cipherkey == "y":
		cipherkey = os.urandom(16)		
		cipherkey_tosend = str (base64.b64encode (cipherkey), "utf8")
		cipher = AES.new (cipherkey, AES.MODE_ECB)
		return cipherkey_tosend, cipher
	
	number = cipherkey.encrypt (bytes("%16d" % number, "utf8"))
	number_tosend = str (base64.b64encode (number), "utf8")
	return number_tosend

# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary strings coded in base64
def decrypt_intvalue (number_recv, cipher):
	number = base64.b64decode (number_recv)
	number = cipher.decrypt (number)
	number = int (str (number, "utf8"))
	return number

# verify if response from server is valid or is an error message and act accordingly
def validate_response (client_sock, response):
	if response["status"] == False:
		return("--- Erro: " + response["error"] + " ---") #  estava print, meti return para testar  
		client_sock.close ()
		sys.exit(3)
	else:
		return True

# process QUIT operation
def quit_action (client_sock, attempts):
	return("--- Desistiu com sucesso ---")
	client_sock.close ()
	sys.exit(4)

def stop_action (client_sock, attempts):
	return("--- Parabéns!!! Terminou o jogo em " + str(attempts) + " tentativas ---")
	client_sock.close ()
	sys.exit(0)

# Outcomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "GUESS", number }
# { op = "STOP", number, attempts }
#
# Incomming message structure:
# { op = "START", status, max_attempts }
# { op = "QUIT" , status }
# { op = "GUESS", status, result }
# { op = "STOP", status, guess }

#
# Suporte da execução do cliente
#

def run_client (client_sock, client_id):
	
	incrip = "y" # para testar o encript
	if(incrip == "INFO" or incrip == "info"):
		response = sendrecv_dict (client_sock, {"op": "INFO"})
		validate_response(client_sock, response)
		print("\n") 
		run_client(client_sock, client_id) #$ para voltar a pedir input, uso de recursividade
		
	if(incrip == "Y" or incrip == "y"):
		cipherkey_tosend, cipher = encrypt_intvalue(incrip, 0)
		response = sendrecv_dict (client_sock, {"op": "START", "client_id": client_id, "cipher": cipherkey_tosend }) ##alteração do client_id de sys... para client_id para testes
		print("*** Tem no maximo ", str(decrypt_intvalue(response["max_attempts"], cipher)), " tentativas ***")
		attempts = 0
		if validate_response(client_sock, response):
			while 1:
				
				m_client = input("--> Faça uma tentativa ou, se desejar, desista(QUIT): ").strip()
				
				if m_client == "QUIT": 
					response = sendrecv_dict (client_sock, {"op": "QUIT"})
					if validate_response(client_sock, response) == True:
						quit_action(client_sock, attempts)

				else:
					try:
						number = int(m_client)
					except (ValueError):
						print("--- Erro: Coloque um numero inteiro entre 0 e 100 ou faça QUIT ---")
						client_sock.close ()
						exit(3)
					number = encrypt_intvalue(cipher, number)
					response = sendrecv_dict (client_sock, {"op": "GUESS", "number": number})
					
					
					if validate_response(client_sock, response):
						attempts = attempts + 1;
						print ("*** %s ***" %(response["result"]))
						if response["result"] == "equals":
							response = sendrecv_dict (client_sock, {"op": "STOP", "number": number, "attempts": encrypt_intvalue(cipher, attempts)})
							validate_response(client_sock, response)
							stop_action(client_sock, attempts)
							break
							
	if(incrip == "N" or incrip == "n"):
		response = sendrecv_dict (client_sock, {"op": "START", "client_id": sys.argv[1], "cipher": None})
		print("*** Tem no maximo " + str(response["max_attempts"]) + " tentativas ***")
		attempts = 0
		if validate_response(client_sock, response):
			while 1:
				
				m_client = input("--> Faça uma tentativa ou, se desejar, desista(QUIT): ").strip() 
				
				if m_client == "QUIT": 
					response = sendrecv_dict (client_sock, {"op": "QUIT"})
					if validate_response(client_sock, response) == True:
						quit_action(client_sock, attempts)

				else:
					try:
						number = int(m_client)
					except (ValueError):
						print("--- Erro: Coloque um numero inteiro entre 0 e 100 ou faça QUIT ---")
						client_sock.close ()
						exit(3)
					
					response = sendrecv_dict (client_sock, {"op": "GUESS", "number": number})
					
					if validate_response(client_sock, response):
						attempts += 1;
						print ("*** %s ***" %(response["result"]))
						if response["result"] == "equals":
							response = sendrecv_dict (client_sock, {"op": "STOP", "number": number, "attempts": attempts})
							validate_response(client_sock, response)
							stop_action(client_sock, attempts)
							break
	else:
		print("--- Erro: introduza apenas [Y/N], ou INFO para mais informação ---")
		sys.exit(2)
	

def main():
	# validate the number of arguments and eventually print error message and exit with error
	# verify type of of arguments and eventually print error message and exit with error

	if len(sys.argv) > 4 or len(sys.argv) < 3 :
		print("--- Erro: numero de argumentos errado (python3 client.py client_id porto [máquina]) ---")
		sys.exit(1)
	
	try:
		port = int(sys.argv[2])
	except ValueError:
		print("--- Erro: Passe um valor de porta do tipo inteiro positivo ---")
		exit(2)
		
	if len(sys.argv) == 3:
		hostname = "127.0.0.1"
	else:
		hostname = sys.argv[3]

	client_sock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	try:
		client_sock.connect ((hostname, port))
	except socket.gaierror:
		print("--- Erro: Passe um valor de hostname valido (ex: \"123.1.2.3\") ---")
		exit(1)
	except OSError:
		print("--- Erro: Impossivel conectar ao servidor, verifique se colocou o valor de hostname correto ---")
		exit(1)

	run_client (client_sock, sys.argv[1])

	client_sock.close ()
	sys.exit (0)
	

if __name__ == "__main__":
    main()

