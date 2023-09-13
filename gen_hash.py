import cryptography
from cryptography.fernet import Fernet
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii
import csv

list1 = [('alice','1234'),('bob','5678'),('tom','9012')]
list2 = []
for item in list1:
    result = hashlib.md5(item[1].encode())
    list2.append((item[0],result.hexdigest()))

with open('passwd.csv', mode='w') as file1:
    writer1 = csv.writer(file1, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for item1 in list2:
        writer1.writerow(item1)
