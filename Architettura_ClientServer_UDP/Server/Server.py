#Elaborato Programmazione ad Oggetti
#Ferri Samuele - Strada Nicola

# Class Server:
# This is the Server class, it is used to handle the operations required by the Client, the Server is
# defined by a default port and a default address. Once the Server is executed, with the appropriate function
# 'start_server', the Server will remain listening for a message of type 'datagram_operation'
# which will define the command and consequently the Server will execute the command: 'home', 'list', 'get',
# 'put', 'close'.
# For each completed operation the Server will send a Datagram with 'file_name' => 'FILE_END', in this way
# will notify to the Client that the executed operation has finished successfully. Otherwise will sent a
# Datagram with 'file_name' => 'ERROR', this to signal the presence of an error during execution, and 
# the consequently aborting the operation.
# The Server uses a specify Datagram, built by the 'MakeDatagram' class, in which it will fill in
# the appropriate fields or read from them, depending by on the operation.

import socket as sk
import time
import os
import sys
import math
import json
import glob
import base64
from Operation import Operation
from MakeDatagram import MakeDatagram
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Server:
    port = 0
    address = ''
    socket = 0
    buffer = 0
    sleep_time = 0
    maker_datagram = MakeDatagram()
    select_operation = Operation()
    files_path = os.path.join(os.getcwd(), 'Server')
    home =  'This is UDP Server, the available operations are the follows: \n' \
            '1. Command "list": used to display all files name saved on the server \n' \
            '2. Command "get": used to download the requested file \n' \
            '3. Command "put": used to upload a file on the server \n' \
            '4. Command "close": to close the Server Connection'

    # Constructor for the Server Class
    def __init__(self):
        self.port = 10000
        self.address = 'localhost'
        self.socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        # Buffer of 9216 byte
        # Buffer size set to 9216 byte, this size can cause errors (Message Too Long) on a MacOS device. 
        # In this case you have to simply reduce the Buffer size (Ex 4096).
        self.buffer = 9216
        self.sleep_time = 0.05
        
    # Check the directory of the Server: if it's not present, will be create a default folder.
    def check_directory(self, name):
        if not os.path.exists(os.path.join(self.files_path, name)):
            os.mkdir(os.path.join(self.files_path, name))
        self.files_path = os.path.join(self.files_path, name)
    
    # After checked the default directory, and initialize the server adress, open the Server and it's start
    # to listen for any message from the Client.
    def start_server(self):
        self.check_directory('Files_Server')
        server_address = (self.address, self.port)
        print ('Starting connection on %s port: %s \n' % server_address)
        self.socket.bind(server_address)
        self.server_opening()

    # Used for close the Server, this close also every connection with every Client.
    def close_server(self):
        print('Server Closed! \n')
        self.socket.close()

    # Used for set the Server in listening and wait for a 'datagram_operation' from the Client.
    def server_opening(self):
        while True:
            self.socket.settimeout(None)
            print('Waiting to receive the operation selected by the Client... \n')
            data, client_address = self.socket.recvfrom(self.buffer)
            datagram_operation = json.loads(data.decode())
            operation_selected = datagram_operation['operation']
            file_name = datagram_operation['file_name']
            if operation_selected == self.select_operation.operation_home():
                self.send_home(client_address)
            elif operation_selected == self.select_operation.operation_list():
                self.command_list(client_address)
            elif operation_selected == self.select_operation.operation_get():
                self.command_get(client_address, file_name)
            elif operation_selected == self.select_operation.operation_put():
                self.command_put(client_address, file_name)

    # Send the datagram encode, passed as a parameter.
    def send_datagram(self, datagram, client_address):
        self.socket.sendto(datagram.encode(), client_address)
        time.sleep(self.sleep_time)
    
    # Send the datagaram error, built with the command that generate the error, and the error string caught.
    def send_datagram_error(self, client_address, command, error):
        file_name = 'ERROR'
        datagram_error = self.maker_datagram.datagram_error(file_name, command, error)
        self.send_datagram(datagram_error, client_address)
        time.sleep(self.sleep_time)
    
    # send_home used to send the home string request from the Client, where will be explained the available 
    # operations and how to use them.
    def send_home(self, client_address):
        file_name = self.select_operation.operation_home()
        datagram = self.maker_datagram.datagram(file_name, sys.getsizeof(self.home), self.home.encode())
        self.send_datagram(datagram, client_address)
    
    # command_list : first command selectable from the Client, the Server send the list with every file name
    #                saved on the Server.
    def command_list(self, client_address):
        file_name = self.select_operation.operation_list()
        files_name = ''
        for file in glob.glob(self.files_path + '/*'):
            files_name +=  ' - ' + file.replace(self.files_path + '/', '') + '\n'
        datagram = self.maker_datagram.datagram(file_name, sys.getsizeof(files_name), files_name.encode())
        self.send_datagram(datagram, client_address)
    
    # command_get : second command selectable from the Client, here the Server start to send, if it's present,
    #               the file define in the file name to the Client.
    #               Each packet sent by the Server is composed of a 'metadata' field, which is at most 9216
    #               bytes. In this way multiple packets will be sent for each file.
    def command_get(self, client_address, file_name):
        try:
            if os.path.isfile(self.files_path + '/' + file_name):
                number_datagram_sent = 0
                file_length = os.stat(self.files_path + '/' + file_name)
                number_datagram_send = math.ceil(file_length.st_size / self.buffer)
                file_send = open(self.files_path + '/' + file_name, 'rb')
                for i in range(number_datagram_send):
                    metadata = file_send.read(self.buffer)
                    datagram = self.maker_datagram.datagram(file_name, sys.getsizeof(metadata), metadata)
                    self.send_datagram(datagram, client_address)
                    number_datagram_sent+= 1
                if number_datagram_sent == number_datagram_send:
                    datagram_end = self.maker_datagram.datagram('FILE_END', 0, 'Receiving of file datagrams is over: Download complete'.encode())
                    self.send_datagram(datagram_end, client_address)
                    print('File sent successfully \n ')
                else:
                    self.send_datagram_error(client_address, self.select_operation.operation_get(), 'Error while sending datagrams'.encode())
                    print('Error while send datagrams: Download Stopped! \n ')
            else:
                self.send_datagram_error(client_address, self.select_operation.operation_get(), 'The file is not present in the Server'.encode())
                print('Error while send datagrams: Download Stopped! \n ')
        except Exception as error:
            self.send_datagram_error(client_address, self.select_operation.operation_get(), (str(error)).encode())
            print('Error while send datagrams: Download Stopped! \n ')

    # command_put : third command selectable from the Client, here the Server start to listen and wait for
    #               the datagrams sent by the Client, for each packet received, the Server read the 'metadata' 
    #               field, decode that with Base64 standard, and write in a new file in the default folder.
    def command_put(self, client_address, file_name):
        buffer_rec = self.buffer * 2
        try:
            file = open(self.files_path + '/' + file_name, 'wb')
            while True:
                datagram_recv = self.socket.recv(buffer_rec)
                metadata_json = json.loads(datagram_recv.decode())
                if 'FILE_END' == metadata_json['file_name']:
                    file.close()
                    print('File reiceved successfully \n ')
                    break
                elif 'ERROR' == metadata_json['file_name']:
                    raise Exception((base64.b64decode(metadata_json['error'])).decode())
                file.write(base64.b64decode(metadata_json['metadata']))
                time.sleep(self.sleep_time)
        except Exception as error:
            os.remove(self.files_path + '/' + file_name)
            print(error)
