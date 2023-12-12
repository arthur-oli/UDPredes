import socket
import hashlib

#localhost
localIP = "127.0.0.1"

#utilizar ipv4 caso LAN
#localIP = "192.168.0.67"

localPort = 20001
bufferSize = 50

#Cria socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
#Binda o socket pro ip e porta do servidor
UDPServerSocket.bind((localIP, localPort))
print("Servidor UDP ouvindo na porta {}".format(localPort))

#Resposta ao cliente
def responder_cliente(fileName, address):
    try:
        with open(fileName, 'rb') as file:
            while data := file.read(1024):

                #Calcula o checksum utilizando md5
                checksum = hashlib.md5(data).digest()

                #Inicializa como NOK para cair no while
                check = 'NOK'
                #Envia o pedaço para o cliente enquanto continuar tendo perda
                while check == 'NOK':
                    UDPServerSocket.sendto(checksum + data, address)
                    check = UDPServerSocket.recvfrom(bufferSize)
                    check = check[0].decode('utf-8')
                    if check == 'NOK': 
                        print('NOK recebido. Reenviando parte do arquivo.')
    
    except FileNotFoundError:
        UDPServerSocket.sendto('FileNotFoundError'.encode('utf-8'), address)
    #Envia vazio para fechar o recebimento no cliente
    UDPServerSocket.sendto(b'', address)

#protocolo, verifica se a mensagem começa com LER
def protocol(message, address):
    messageString = message.decode('utf-8')

    print("Endereço IP do cliente: {}. Mensagem: {}".format(address, messageString))

    if messageString.startswith('LER '):
        fileName = messageString[4:]
        responder_cliente(fileName, address)


#faz uma lista de endereços já conectados para garantir que possa responder a vários clientes
def main():
    addresses = []
    while True:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        if(bytesAddressPair[1] not in addresses):
            addresses.append(bytesAddressPair[1])
            protocol(bytesAddressPair[0], bytesAddressPair[1])

if __name__ == '__main__':
    main()