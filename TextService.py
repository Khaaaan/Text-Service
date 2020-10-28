import socket
import argparse
import pickle
import os
import json
import string


class Server:

    def __init__(self,interface, port):
        self.interface = interface
        self.port = port

    
    # to start the server
    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.interface, self.port))
        self.sock.listen(10)
        print('Listeining at', self.sock.getsockname())

        # flag for counting whether it will be encode or decode
        self.n = 0 
        # first time the server run,  this flag will be zero
        # odd numbers denote encode
        # even ones denote decode
        while True:
            self.receive()
            self.identifyMode()
            self.sendBack()
            self.sc.close()

    # receive data 
    def receive(self):
        self.sc, self.sockname = self.sock.accept()
        print('Acceppted connection from', self.sockname)
        self.finalData = b''
        while True:
            data = self.sc.recv(1024)
            if not data:
                break
            self.finalData += data
        self.myPickledObject = self.finalData
        self.myUnpickledObject = pickle.loads(self.myPickledObject)


    # identify mode from data received
    def identifyMode(self):
        self.mode = self.myUnpickledObject.getMode()
        if self.mode == 'encode_decode':
            # count encode_decode mode
            self.n += 1
            self.mode = 'encrypt' if self.n % 2 != 0 else 'decrypt'
        
        modeDict = { 'change_text': self.changeText, 'encrypt': self.encText, 'decrypt': self.decText}
        
        self.function = modeDict[self.mode]


    # send modified data back to the client
    def sendBack(self):
        data = self.function(self.myUnpickledObject)
        self.sc.send(data)
        

    def changeText(self, myObject):
        text = myObject.getFirstFile()
        jsonString = myObject.getSecondFile()
        pythonObj = json.loads(jsonString)

        for key in pythonObj:
            modifiedText = text.replace(key, pythonObj[key])
            text = modifiedText
        return text.encode('utf-8')


    def encText(self,myObject):
        alphabet = string.ascii_letters
        ciphertext = ''

        plainText = myObject.getFirstFile()
        key = myObject.getSecondFile()
        while len(key)< len(plainText):
            key += key
        
        for i, char in enumerate(plainText):
            if char not in alphabet:
                ciphertext += char
                continue
            charId = alphabet.index(char)
            keyId = alphabet.index(key[i])

            cipher = (charId + keyId) % len(alphabet)
            ciphertext += alphabet[cipher]
        
        return ciphertext.encode('utf-8')


    def decText(self,myObject):
        alphabet = string.ascii_letters
        plainText = ''

        cipherText = myObject.getFirstFile()
        key = myObject.getSecondFile()
        while len(key)< len(cipherText):
            key += key
        
        for i, char in enumerate(cipherText):
            if char not in alphabet:
                plainText += char
                continue
            charId = alphabet.index(char)
            keyId = alphabet.index(key[i])

            decipher = (charId - keyId) % len(alphabet)
            plainText += alphabet[decipher]

        return plainText.encode('utf-8')

            

class Client:
    
    def __init__(self, hostname, port,file):
        self.hostname = hostname
        self.port = port
        self.file = file

    

    # to start the client 
    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.hostname, self.port))
        self.sendFiles()
        self.getFile()

        # delete buff file which was created for pickled data
        if os.path.exists(self.file):
            os.remove(self.file)
            
        self.sock.close()


    # send files
    def sendFiles(self):
        f = open(self.file, 'rb')
        while True:
            data = f.read(1024)
            if not data:
                break
            self.sock.send(data)
        f.close()
        self.sock.shutdown(socket.SHUT_WR)


    
    # get modified file
    def getFile(self):
        finalData = b""
        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            finalData += data

        f = open('server_response.txt', 'wb')
        f.write(finalData)
        f.close()

        

# Pickling python object into the 'buff' file
def makePickleFile(mode, file1, file2):
    myObject = database(mode, file1, file2)
    myObject.setFirstFile()
    myObject.setSeecondFile()
    with open('buff','wb') as write_file:
        pickle.dump(myObject, write_file)



# class for saving our files
class database:
    def __init__(self, mode, file1, file2):
        self.mode = mode
        self.file1 = file1
        self.file2 = file2


    def setFirstFile(self):
        self.text = ''
        f = open(self.file1,'r')
        while True:
            data = f.read(1024)
            if not data:
                break
            self.text += data
        f.close()

    def setSeecondFile(self):
        self.secondText = ""
        f = open(self.file2, 'r')
        while True:
            data = f.read(1024)
            if not data:
                break
            self.secondText += data      
        f.close()


    def getFirstFile(self):
        return self.text

    def getSecondFile(self):
        return self.secondText

    def getMode(self):
        return self.mode


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='send object with pickle to server')
    parser.add_argument('--server',action='store_true',help = ' Run as server')
    parser.add_argument('--hostname', default='127.0.0.1',
                        help = 'IP address or hostname ( default = %(default)s )')
    parser.add_argument('--port',type= int, default=1060,
                        help='TCP port number ( default: %(default)s )')    
    parser.add_argument('--mode',choices=['change_text','encode_decode'],
                        help = ' Choose the mode if you (run as client)')
    parser.add_argument('file',nargs='*', help='input files which will be sent to server for processing')
    args =parser.parse_args()
    
    if (len(args.file) < 2 and args.mode) or ( args.file and not args.mode):
        parser.error(' 2 files should be provided with mode')


    if args.server:
        object = Server(args.hostname, args.port)
    else:
        makePickleFile(args.mode, args.file[0], args.file[1])
        # pass pickled buff file to the client
        object = Client(args.hostname, args.port, 'buff')

    object.start()
