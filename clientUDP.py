import socket
import hashlib
import random
from _thread import *

def verificar_checksum(data_with_checksum):
    # O primeiro bloco de 16 bytes é o checksum
    checksum = data_with_checksum[:16]
    # O restante são os dados
    data = data_with_checksum[16:]
    
    # Calcula o checksum dos dados recebidos
    checksum_calculado = hashlib.md5(data).digest()
    
    # Compara os checksums
    return checksum == checksum_calculado


# localhost
serverAddressPort = ("127.0.0.1", 20001)

# utilizar ipv4 do server caso for em LAN
# serverAddressPort = ("192.168.0.67", 20001)

bufferSize = 1040

fileName = input("Digite o o nome do arquivo + extensão: ")
bytesToSend = str.encode('LER ' + fileName)

opcao = input("Simular perda de parte do arquivo? (S/N): ").upper()

# Range para "perda de pacote", descartado uma parte do arquivo
r = random.randrange(16, 1024)
l = random.randrange(r + 1, 1024)
perda = random.randrange(1, 10)
    
# Cria um socket UDP do lado do cliente
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Envia pro servidor utilizando o socket UDP
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

# Nome do arquivo a ser salvo
newFileName = 'new' + fileName 

# Cria o arquivo para escrita
full_file = ""

# Contador de chunks recebidos
chunkCount = 0

while True:
    #Recebe um pedaço do arquivo
    data_with_checksum, _ = UDPClientSocket.recvfrom(bufferSize)
   
    #Se não há mais dados, saia do loop
    if not data_with_checksum:
        break
    
    #Conta número de chunks recebidos
    chunkCount += 1
    if opcao == 'S' and chunkCount == perda:
        data_with_checksum = data_with_checksum[:16] + data_with_checksum[16:r] + data_with_checksum[r+1:l]
        opcao = 'N'
        
    #Verifica se o checksum recebido bate com o calculado, se não, pede reenvio
    if verificar_checksum(data_with_checksum):
        #Remove os primeiros 16 bytes (checksum) e escreve o restante no arquivo
        full_file += data_with_checksum[16:].decode('utf-8')
        check = 'OK' 
    else:
        print("Erro de checksum na parte {}. Uma parte do arquivo foi perdida. Requisitando reenvio.".format(chunkCount))
        check = 'NOK'

    #Envia o check (OK ou NOK) para o servidor.
    checkEncoded = str.encode(check)
    UDPClientSocket.sendto(checkEncoded, serverAddressPort)

#Escreve no arquivo
print("Escrevendo dados no arquivo {}".format(newFileName))
with open(newFileName, 'w') as file:
    file.write(full_file)

#Fecha conexão
print("Finalizado. Fechando conexão com o servidor.")
UDPClientSocket.close()