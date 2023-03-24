#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time
import numpy as np
from datetime import datetime




serialName = "COM5"                  # Windows(variacao de)


def main():
    try:


        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        com1.enable()
        time.sleep(.2)
        com1.sendData(b'\x00')
        time.sleep(1)

        inicio = False

        #Arquivo

        arq = open("data/Client2.txt", "x")

        server_id = b'\xEE'

        img_id = b'\xcc'

        eop = b'\xAA\xBB\xCC\xDD'

        #Numero total de Pacotes

        imageR = "pequeno.png"

        txBuffer = open(imageR, 'rb').read() #isso é um array de bytes

        imagem = len(txBuffer)  # numero de bits
        pacotes_completos = imagem // 114
        pacote_restante = imagem % 114

        if pacote_restante == 0 : 
            total_de_pacotes = pacotes_completos
        else:
            total_de_pacotes = pacotes_completos + 1

        print("numero de pacotes:{}".format(total_de_pacotes))

        

        handshake = b'\x01' + server_id + b'\x00' + total_de_pacotes.to_bytes(1, byteorder='big') + b'\x00' + img_id + b'\x00'*4 + eop


        while not inicio:
            print("Enviando handshake")

            com1.sendData(handshake)
            arq.write(f"{datetime.now()} / envio / 1 / {len(handshake)}\n")

            time.sleep(5)
            print(f"Rx len: {com1.rx.getBufferLen()} antes")
            if com1.rx.getBufferLen() > 0:
                tamanho = com1.rx.getBufferLen()
                rxBuffer, nRx = com1.getData(14) #Pegando o tipo de mensagen
                print(rxBuffer)
                if rxBuffer[0] == 2:
                    inicio = True
                    print("Handshake recebido")
                    arq.write(f"{datetime.now()} / receb / 2 / {tamanho}\n")
                    print(f"Rx len: {com1.rx.getBufferLen()} depois")
                else:
                    print("Erro na resposta do handshake")
            else:
                print("Handshake não recebido")
           
        i = 1
        timer1 = time.time()

        timer2 = time.time()
        while i < total_de_pacotes:
            
            com1.rx.clearBuffer()
            pacote_full = bytearray()
            pacote_full_arrumado = bytearray()

            print(f"rxBuffer len: {com1.rx.getBufferLen()}limpo")

            payload = txBuffer[i*114:(i+1)*114]
            len(payload).to_bytes(1, byteorder='big')
            pacote_full += b'\x03' + b'\x00' + b'\x00' + total_de_pacotes.to_bytes(1, byteorder='big') + i.to_bytes(1, byteorder='big') + len(payload).to_bytes(1, byteorder='big') + b'\x00'*4 + payload + eop

            com1.sendData(pacote_full)
            
            arq.write(f"{datetime.now()} / envio / 3 / {len(pacote_full)} / {i} / {total_de_pacotes} / 00 \n")
            print("Pacote {} enviado" .format(i))
            
            print("-"*50)

            time.sleep(1)
            
            if com1.rx.getBufferLen() > 0:
                print("Recebendo pacote")
                rxBuffer, nRx = com1.getData(14) #Tipo de mensagem
                print(f"{rxBuffer[0]} recebido")
                print(f"valor da i: {i} e valor do rxBuffer[6]: {rxBuffer[6]}")
                if rxBuffer[6] == i and rxBuffer[0] == 4:
                    print("Pacote {} recebido" .format(i))
                    arq.write(f"{datetime.now()} / receb / 4 / {nRx} \n")
                    i += 1
                    timer1 = time.time()
                    timer2 = time.time()
                else:
                    i = rxBuffer[6]

                
            else: 
                print("-"*50)
                print("4 nao recebido")
                print("-"*50)
                tempo = -timer1 + time.time()
                tempo_2 = time.time() - timer2 
                print (f"tempo 2:{tempo_2}")
                if tempo > 5:
                    print("Pacote {} não recebido" .format(i))
                    com1.sendData(pacote_full)
                    arq.write(f"{datetime.now()} / envio / 3 / {len(pacote_full)} / {i} / {total_de_pacotes} / 00 \n")
                    time.sleep(1)
                    timer1 = time.time()

                elif tempo_2 > 20:

                        print("Timeout")
                        timeout = b'\x05' + b'\x00' + b'\x00' + total_de_pacotes.to_bytes(1, byteorder='big') + b'\x00' + b'\x00' + b'\x00'*4 + eop
                        com1.sendData(timeout)
                        time.sleep(1)
                        arq.write(f"{datetime.now()} / envio / 5 / {len(timeout)} \n")

                        raise Exception("Timeout - Tempo de resposta excedido")
                else:
                    if com1.rx.getBufferLen() > 0:
                        rxBuffer, nRx = com1.getData(14) #Tipo de mensagem
                        if rxBuffer[0] == 6:
                            print("-"*50)
                            print("Tipo de mensagem 6")	
                            print("-"*50)
                            cont = rxBuffer[6]
                            i = rxBuffer[6]
                            payload = txBuffer[i*114:(i+1)*114]
                            pacote_full_arrumado += b'\x03' + b'\x00' + b'\x00' + total_de_pacotes.to_bytes(1, byteorder='big') + cont.to_bytes(1, byteorder='big') + len(payload).to_bytes(1, byteorder='big') + b'\x00'*4 + payload + eop
                            com1.sendData(pacote_full_arrumado)
                            time.sleep(1)
                            arq.write(f"{datetime.now()} / envio / 3 / {len(pacote_full_arrumado)} / {cont} / {total_de_pacotes} / 00 \n")
                            timer1 = time.time()
                            timer2 = time.time()           

        arq.close()

    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()


        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()

