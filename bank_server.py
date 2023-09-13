import socket
import ssl
import sys
import cryptography
from cryptography.fernet import Fernet
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii
from _thread import *
import json 
import csv

HOST = socket.gethostbyname(socket.gethostname())
PORT = int(sys.argv[1])
ADDR = (HOST, PORT)
tcount = 0
flag = 0
check_cred = 0
decpt_uid = ''

f = open('balance.json')
dict1 = json.load(f)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

#read server private key
file2 = open('Kprb.key', 'r')
prbkey = file2.read()
file2.close()
serv_private = RSA.importKey(prbkey)

server.bind((HOST, PORT))
server.listen(10)

print(f"SERVER LISTENIING TO CLIENT CONNECTIONS ON {ADDR}")

def func_try(decpt_symmKey):
    global decpt_uid

    fernet1 = Fernet(decpt_symmKey)

    uid = connection.recv(1024)
    decpt_uid = fernet1.decrypt(uid)

    pswd = connection.recv(1024)
    decpt_pswd = fernet1.decrypt(pswd)

    flag = 0 

    with open('passwd.csv', mode ='r')as file:
        
        list1 = csv.reader(file)
        
        for item in list1:
            if item[0] == decpt_uid.decode("utf-8"):

                paswds = decpt_pswd.decode("utf-8")
                hash_paswd = hashlib.md5(paswds.encode())
                
                if item[1] == hash_paswd.hexdigest():
                    flag = 1

    if flag == 0:
        print("\nDETAILS NOT MATCHED")

    connection.send(str(flag).encode("utf-8"))
    return flag

def multiple_client(connection):
    while True:
        
        check_cred = 0

        data = connection.recv(1024)
        print("\nENCRYPTED SYMMETRIC KEY RECEIVED")
        if not data:
            break

        #decrypt symmetric key with server private key
        decryptor = PKCS1_OAEP.new(serv_private)
        decpt_symmKey = decryptor.decrypt(data)

        while check_cred == 0 :
            check_cred = func_try(decpt_symmKey)
        
        if check_cred == 1:

            print("\nDETAILS MATCHED ")
            while True:
                option = connection.recv(1024)
                
                if option.decode("utf-8") == '1':

                    receiver_uid = (connection.recv(1024)).decode("utf-8")

                    amt = (connection.recv(1024)).decode("utf-8")

                    sender_uid = decpt_uid.decode("utf-8")

                    if receiver_uid in dict1:

                        if dict1[sender_uid] >= int(amt):
                            #print("Sufficient balance available so deduct")
                            dict1[sender_uid] = dict1[sender_uid] - int(amt)
                            dict1[receiver_uid] = dict1[receiver_uid] + int(amt)
                            #print(dict1)

                            temp = json.dumps(dict1)
                            with open("balance.json", "w") as writefile:
                                writefile.write(temp)
    
                            connection.send(b"1")
                            
                        else:
                            print("\nSUFFICIENT BALANCE NOT AVAILABLE")
                            connection.send(b"0")
                    
                    else:
                        print("\nRECEIVER INCORRECT")
                        connection.send(b"2")
                
                else: 
                    connection.close()
                    break
   
        break
    connection.close()
    print(f"\nSERVER LISTENIING TO CLIENT CONNECTIONS ON {ADDR}")

    

while True:
    #print("SERVER IS LISTENING in first while")
    connection, client_address = server.accept()
    print("\nClient connected: {} : {}".format(client_address[0], client_address[1]))
    start_new_thread(multiple_client,(connection, ))
    tcount += 1
    #print("Thread count : " + str(tcount))

server.close()





            
