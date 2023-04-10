#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socket
import select
import json
import base64
import csv
import random
from common_comm import send_dict, recv_dict, sendrecv_dict

from Crypto.Cipher import AES

# Dicionário com a informação relativa aos cliente
gamers = {"Manel": {"socket": "abc", "guess": 60, "max_attempts": 20, "attempts": 20, "cipher": None}}

# return the client_id of a socket or None
def find_client_id (client_sock):
	key_list = list(gamers.keys())
	val_list = list(gamers.values())
	
	for v, k in zip(val_list, key_list):
		if v["socket"] == client_sock:
			return k
			
	return False # $ returns false when the client is not registed in the dictionary $


# Função para encriptar valores a enviar em formato json com codificação base64
# return int data encrypted in a 16 bytes binary string and coded base64
def encrypt_intvalue (cipherkey_recv, number):
	cipherkey = base64.b64decode (cipherkey_recv)
	cipher = AES.new (cipherkey, AES.MODE_ECB)
	
	number = cipher.encrypt (bytes("%16d" % number, 'utf8'))
	number_tosend = str (base64.b64encode (number), 'utf8')
	
	return number_tosend


# Função para desencriptar valores recebidos em formato json com codificação base64
# return int data decrypted from a 16 bytes binary string and coded base64
def decrypt_intvalue (number, cipherkey_rec):
	cipherkey = base64.b64decode (cipherkey_rec)
	cipher = AES.new (cipherkey, AES.MODE_ECB)
	number_dec = base64.b64decode (number)
	number_dec = cipher.decrypt (number_dec)
	number_dec = int (str (number_dec, 'utf8'))
	return number_dec



#
# Incomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "GUESS", number }
# { op = "STOP", number, attempts }
#
# Outcomming message structure:
# { op = "START", status, max_attempts }
# { op = "QUIT" , status }
# { op = "GUESS", status, result }
# { op = "STOP", status, guess }


#
# Suporte de descodificação da operação pretendida pelo cliente
#
def new_msg (client_sock):
	res = recv_dict (client_sock)
	
	if res["op"] == "START":
		send_dict (client_sock, new_client(client_sock, res))   
	elif res["op"] == "QUIT":
		send_dict (client_sock, quit_client(client_sock, res))  
	elif res["op"] == "GUESS":
		send_dict (client_sock, guess_client(client_sock, res)) 
	elif res["op"] == "STOP":
		send_dict (client_sock, stop_client(client_sock, res))
	elif res["op"] == "INFO":
		send_dict (client_sock, {"op": "INFO", "status": True})  #$ é enviado como mensagem para a aplicação do cliente de forma a dizer que não ocorreram erros
		                                                                    #$ mas não é imprimida, porque acho que esteticamente não faria sentido, apenas iria confundir mais o cliente
		print("\n""   ----- INFO -----   \n" "\n" "Objetivo do jogo:\n" "\n" "Irá lhe ser atribuido um numero maximo de jogadas,\n" "o seu objetivo é, dentro desse limite, encontrar o numero secreto\n" "que está compreendido entre 0 e 100 \n"\
		"\n" "Como jogar:\n" "\n" "1- Escolha se quer que as suas mensagens sejam encriptadas ao serem enviadas para o servidor\n" "2- Tente advinhar o numero, digitando o valor \n" "3- Se em algum momento pretender disistir, digite QUIT \n" \
		"4- Por fim, quando acertar, será lhe apresentado uma mensagem final\n" "5- Se ultrapassar o maximo de jogadas, quando descobrir o numer será lhe apresentado uma mensagem de erro \n \n"\
		"   ----- INFO -----   ")
		
	else:                                                                  #$ erro, ocorre quando a operação não existe
		response = send_dict (client_sock, {"op":res["op"], "status": False, "error": "Operação inexistente (operações possivesis: \"START\", \"GUESS\", \"QUIT\", \"STOP\")"}) 
# read the client request
# detect the operation requested by the client
# execute the operation and obtain the response (consider also operations not available)
# send the response to the client


#
# Suporte da criação de um novo jogador - operação START
#
def new_client (client_sock, request):
	if len(gamers) != 0:   #$ se o dicionario gamers não estiver vazio
		key_list = list(gamers.keys())
		for k in key_list:
			if k == request["client_id"]:
				return { "op": "START", "status":False, "error": "cliente existente" }
				
	if request["cipher"]!= None:
		gamers[request["client_id"]] = {"socket": client_sock, "guess": random.randint(0,100) , "max_attempts": random.randint(10,30), "attempts": 0, "cipher": request["cipher"] }
		return { "op": "START", "status":True, "max_attempts": encrypt_intvalue(gamers[request["client_id"]]["cipher"], gamers[request["client_id"]]["max_attempts"])}
	else:
		gamers[request["client_id"]] = {"socket": client_sock, "guess": random.randint(0,100) , "max_attempts": random.randint(10,30), "attempts": 0, "cipher": None }
		return { "op": "START", "status":True, "max_attempts": gamers[request["client_id"]]["max_attempts"] }
		
# detect the client in the request
# verify the appropriate conditions for executing this operation
# obtain the secret number and number of attempts
# process the client in the dictionary
# return response message with results or error message


#
# Suporte da eliminação de um cliente
#
def clean_client (client_sock):
	result = gamers.pop(find_client_id(client_sock), -1)
	if result == -1:
		return False #$ return true if the client exists in the dictionary, if not, return false 
	return True
	
# obtain the client_id from his socket and delete from the dictionary


#
# Suporte do pedido de desistência de um cliente - operação QUIT
#
def quit_client (client_sock, request):
	client_id = find_client_id(client_sock)
	if client_id != False: #$ se o cliente está registado no dicionario
		update_file(client_id, "Quit")
		sucess = clean_client(client_sock)
		return { "op": "QUIT", "status":True}
	else: 
		return { "op": "QUIT", "status":False, "error": "cliente inxistente" }
		
# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# process the report file with the QUIT result
# eliminate client from dictionary
# return response message with result or error message


#
# Suporte da criação de um ficheiro csv com o respectivo cabeçalho
#
def create_file ():
	with open("report.csv", mode="w") as report:
		report = csv.writer(report, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		report.writerow(["Nome", "N secreto", "Tentativas max", "N tentativas", "Resultado"])
		
# create report csv file with header


#
# Suporte da actualização de um ficheiro csv com a informação do cliente e resultado
#
def update_file (client_id, result):
	reader = csv.DictReader(open("report.csv"))
	headers = reader.fieldnames
	report_writer = csv.DictWriter(open("report.csv", 'a' ), headers)
	report_writer.writerow({
				"Nome":client_id, 
				"N secreto": gamers[client_id]["guess"], 
				"Tentativas max": gamers[client_id]["max_attempts"],
				"N tentativas": gamers[client_id]["attempts"], 
				"Resultado": result})
				
# update report csv file with the result from the client


#
# Suporte da jogada de um cliente - operação GUESS
#
def guess_is_correct(guess, client_id): 
	if(guess == gamers[client_id]["guess"]):
		return "equals" 
	if(guess > gamers[client_id]["guess"]):
		return "larger" 
	return "smaller"
	
def guess_client (client_sock, request):
	client_id = find_client_id(client_sock)
	
	if client_id == False:
		return { "op": "GUESS", "status":False, "error": "Cliente inexistente" }
		
	try:
		if gamers[client_id]["cipher"] != None :
			number = decrypt_intvalue(request["number"], gamers[client_id]["cipher"])
		else:
			number = int(request["number"])
	except ValueError:
		return { "op": "GUESS", "status":False, "error": "Tem de inserir um valor do tipo inteiro positivo" }
			
	if number<0 or number>100:
		return { "op": "GUESS", "status":False, "error": "Valor fora dos limites (0 <= number <= 100)" }
	
	gamers[client_id]["attempts"] += 1
	return { "op": "GUESS", "status":True, "result": guess_is_correct(number, client_id ) }
	
# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# return response message with result or error message


#
# Suporte do pedido de terminação de um cliente - operação STOP
#
def stop_client (client_sock, request):
	client_id = find_client_id(client_sock)
	clint_final_guess = " "
	
	if client_id == False:
		return { "op": "STOP", "status":False, "error": "Cliente inexistente" }
		
	if gamers[client_id]["cipher"] != None :
		clint_final_guess = decrypt_intvalue(request["number"], gamers[client_id]["cipher"] )
		request["attempts"] = decrypt_intvalue(request["attempts"], gamers[client_id]["cipher"] )
	else:
		clint_final_guess = request["number"]
		
	if request["attempts"] != gamers[client_id]["attempts"]:
		#update_file(client_id, "Failure")
		return { "op": "STOP", "status":False, "error": "Numero de jogadas inconsistente" }
	if gamers[client_id]["attempts"] > gamers[client_id]["max_attempts"]:
		#update_file(client_id, "Failure")
		return { "op": "STOP", "status":False, "error": "Excedeu o numero maximo de tentativas" }
		
	right_guess = gamers[client_id]["guess"]
	if guess_is_correct(clint_final_guess, client_id)=="equals":
		update_file(client_id, "Sucess") 
	else:
		update_file(client_id, "Failure")
	
	clean = clean_client(client_sock)
	
	if clean: 
		return { "op": "STOP", "status":True, "guess": right_guess}
# obtain the client_id from his socket
# verify the appropriate conditions for executing this operation
# process the report file with the SUCCESS/FAILURE result
# eliminate client from dictionary
# return response message with result or error message


def main():
	# validate the number of arguments and eventually print error message and exit with error
	# verify type of of arguments and eventually print error message and exit with error
	if len(sys.argv) != 2:
		print("--- Erro: numero errado de argumentos (comando correto: python3 server.py porto) ---")
		exit(1)
	
	try:
		port = int(sys.argv[1])
	except ValueError:
		print("--- Erro: passe um valor de porto do tipo inteiro positivo ---")
		exit(2)
		
	server_socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind (("127.0.0.1", port))
	server_socket.listen (10)

	clients = []
	create_file ()

	while True:
		try:
			available = select.select ([server_socket] + clients, [], [])[0]
		except ValueError:
			# Sockets may have been closed, check for that
			for client_sock in clients:
				if client_sock.fileno () == -1: client_sock.remove (client) # closed
			continue # Reiterate select

		for client_sock in available:
			# New client?
			if client_sock is server_socket:
				newclient, addr = server_socket.accept ()
				clients.append (newclient)
			# Or an existing client
			else:
				# See if client sent a message
				if len (client_sock.recv (1, socket.MSG_PEEK)) != 0:
					# client socket has a message
					##print ("server" + str (client_sock))
					new_msg (client_sock)
				else: # Or just disconnected
					clients.remove (client_sock)
					clean_client (client_sock)
					client_sock.close ()
					break # Reiterate select

if __name__ == "__main__":
	main()
