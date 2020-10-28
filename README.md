# Text Service
Simple socket application created with python socket module.
## Table of contents
* [Description](#description)
* [Perequisites](#perequisites)
* [Installation](#installation)
* [Usage](#usage)
    + [Server](#server)
    + [Client](#client)
        * [change_text](#change_text)
        * [encode_decode](#encode_decode)
## Description
Client-server-based console app “text_service”. With the next abilities:

Change text: The sender sends the text file to the server and the json file, in respond the server must read the json file and swap the words from the text according the json file.

Encode/Decode text: The sender sends the text file and the key (another text) on the respond the server must XOR the text message with the key [One Time Pad cipher](https://en.wikipedia.org/wiki/One-time_pad) and return it to the client. The decoding process happens in the same way where instead of the text message the client sends ciphered text.


## Perequisites 
* Python 3.8
* Pickle module protocol version 5

## Installation

To download this repository you should use `git clone` command in your terminal.

```bash
git clone https://github.com/Khaaaan/Text-Service.git
```

After downloading this repository, to install requirements to launch this application you can use `pip install` command in repository directory.

```bash
pip install requirements.txt
```
## Usage
You can run this application as server or client.

    usage: TextService.py [-h] [--server] [--hostname HOSTNAME] [--port PORT]
                    [--mode {change_text,encode_decode}]
                    [file [file ...]]

    send object with pickle to server

    positional arguments:
      file                  input files which will be sent to server for
                            processing

    optional arguments:
      -h, --help            show this help message and exit
      --server              Run as server
      --hostname HOSTNAME   IP address or hostname ( default = 127.0.0.1 )
      --port PORT           TCP port number ( default: 1060 )
      --mode {change_text,encode_decode}
                            Choose the mode if you (run as client)
### Server
To receive and process and finally send back all received data, server should be always running at the background. To run apllication as ***server*** enter this in command line
```bash
python TextService.py --server
```
### Client
Client could use one of two different modes: \
*change_text* 

    --mode change_text

 *encode_decode*
    
    --mode encode_decode
#### change_text
In this mode client sends two different files one of them is text file and another one is json dictionary. Server will change every intersecting word in text with suitable word from json file.\
To run this application in this mode:
```bash
python TextService.py --mode change_text demofile.txt keyfile.json
```
#### encode_decode
In this mode client sends two different files one of them should be plaintext or ciphered text ( depends on server) and otp_key.txt to cipher or decipher.\
The server logic is a making encrypting and decrypting one-by-one. It means if last time server did encryption, this time it will be decyprion or vice versa.
> Therefore in last encode_decode mode you have sent plaintext, now you should send ciphertext.

To run this application in this mode:
```bash
python TextService.py --mode encode_decode plaintext.txt otp_key.txt
```

```bash
python TextService.py --mode encode_decode ciphertext.txt otp_key.txt
```