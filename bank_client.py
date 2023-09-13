import socket
import ssl
import sys
import cryptography
from cryptography.fernet import Fernet
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii
import json

HOST = sys.argv[1]
PORT = int(sys.argv[2])
ADDR = (HOST, PORT)

f = open('balance.json')
dict1 = json.load(f)

check_cred = '0'
uid = ''

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM,0)

#read server public key
file1 = open('Kpub.key', 'r')
pubkey = file1.read()
file1.close()
symm_key = Fernet.generate_key()

#fernet obj to encrypt uid and password
fernet = Fernet(symm_key)

#encrypt symmetric key with server public key 
serv_public = RSA.importKey(pubkey)
encryptor = PKCS1_OAEP.new(serv_public)

#send below encrypted symmetric key to server
enc_symmKey = encryptor.encrypt(symm_key)

def func_try():
    global uid
    uid = input('\nEnter User ID : ')
    enc_uid = fernet.encrypt(bytes(uid, 'utf-8'))

    client.send(enc_uid)

    pwds = input('Enter Password : ')
    enc_pass = fernet.encrypt(bytes(pwds, 'utf-8'))

    #send encrypted password
    client.send(enc_pass)
    
    check_cred = client.recv(1024)
    if check_cred.decode("utf-8") == '0':
        print("\nINCORRECT CREDENTIALS")
    return check_cred.decode("utf-8")


if __name__ == "__main__":
    client.connect((HOST, PORT))
    print("Client side starts")
    print("\nSend encrypted symmetric key to server")
    client.send(enc_symmKey)

    while check_cred == '0':
        check_cred = func_try()

    if check_cred == '1':

        print("\nCREDENTIALS VERIFIED ")
        
        if uid in dict1 :
            print("Your account balance is " +str(dict1[uid]))
            while True:
                option = input("\nPlease select one of the following actions:\n1. Transfer\n2. Exit\n>>>> ")
                client.send(option.encode("utf-8"))

                if option == '1':

                    send_to = input('\nEnter User ID to which money is transfer : ')
                    client.send(send_to.encode("utf-8"))

                    amt = input('Enter Amount to transfer : ')
                    client.send(amt.encode("utf-8"))

                    stat = (client.recv(1024)).decode("utf-8")

                    if stat == '1':
                        print("\nYour transaction is successful !!!!! ")
                        f = open('balance.json')
                        dict2 = json.load(f)
                        print("Updated balance for sender " + str(uid) + " is : " + str(dict2[uid]))
                        print("Updated balance for receiver " + str(send_to) + " is : " + str(dict2[send_to]))
                    elif stat == '2':
                        print("\nRECEIVER INCORRECT")
                    else:
                        print("\nYour transaction is unsuccessful.")

                if option == '2' :
                    print("\nClose connection socket")
                    client.close()
                    break
    client.close()