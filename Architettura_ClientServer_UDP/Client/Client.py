#Elaborato Programmazione ad Oggetti
#Ferri Samuele - Strada Nicola

# Class Client:
#
# This is the Client class, it will be used as an interface for the user, where with
# four predefined commands, will be able to interact with the Server:
# - Command 'list' => This command will allow the Client to display the complete list of names of all
#                     files that are present on the Server.
# - Command 'get' => This command will next request the Client to enter the full name of the file to be
#                    download, in case the file is present on the Server, it will start downloading, and 
#                    once finished you will be able to find the file in the Client's default folder. 
#                    Otherwise, if errors occur during the download, the operation will be cancelled.
# - Command 'put' => This command, similarly to 'get', will require, once selected, write the full name of 
#                    the file from those available, but these must already be found in the folder of the 
#                    Client, if the file is present, it will start the upload operation to the Server. 
#                    Similar to the 'get' operation, in case errors occur, the operation will be cancelled and
#                    the error will be reported.
# - Command 'close' => the last available command is the 'close', which will terminate and close the 
#                      communication with the Server.

import socket as sk
import time
import os
import glob
import base64
import sys
import json
import math
from MakeDatagram import MakeDatagram
from Operation import Operation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Client:
    port_server = 0
    address_server = ''
    buffer = 0
    socket = 0
    sleep_time = 0
    socket_timeout = 0
    maker_datagram = MakeDatagram()
    select_operation = Operation()
    files_path = os.path.join(os.getcwd(), 'Client')
    
    # Constructor for Client Class
    def __init__(self):
        self.port_server = 10000
        self.address_server = 'localhost'
        self.buffer = 9216 #Buffer of 9216 byte
        self.socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.sleep_time = 0.05
        self.socket_timeout = 10

    # Check the directory of the Client: if it's not present, will be create a default folder.
    def check_directory(self, name):
        if not os.path.exists(os.path.join(self.files_path, name)):
            os.mkdir(os.path.join(self.files_path, name))
        self.files_path = os.path.join(self.files_path, name)
    
    # Send the datagram encode, passed as a parameter.
    def send_datagram(self, datagram):
        self.socket.sendto(datagram.encode(), (self.address_server, self.port_server))
        time.sleep(self.sleep_time)
    
    # Send the datagaram error, built with the command that generate the error, and the error string caught.
    def send_datagram_error(self, command, error):
        file_name = 'ERROR'
        datagram_error = self.maker_datagram.datagram_error(file_name, command, error)
        self.send_datagram(datagram_error)
        time.sleep(self.sleep_time)
    
    # list_file_client used to display all the file present in the default folder of the Client.
    def list_files_client(self):
        files_name = []
        for file in glob.glob(self.files_path + '/*'):
            files_name.append(file.replace(self.files_path + '/', ''))
        return files_name
    
    # get_home_server used to request the home from the Server, where will be explained the available 
    # operations and how to use them.
    def get_home_server(self):
        try:
            datagram_operation = self.maker_datagram.datagram_operation('', self.select_operation.operation_home())
            self.send_datagram(datagram_operation)
            self.socket.settimeout(self.socket_timeout)
            datagram_recv = self.socket.recv(self.buffer)
            metadata_json = json.loads(datagram_recv.decode())
            if metadata_json['file_name'] == self.select_operation.operation_home():
                home = (base64.b64decode(metadata_json['metadata'])).decode()
                return home
            else:
                raise Exception('Datagrams decoding error: inconsistent buffer')
        except Exception as error:
            raise Exception('\nError: ' + str(error))
    
    # command_list : first command selectable from the Client.
    def command_list(self):
        try:
            datagram_operation = self.maker_datagram.datagram_operation('', self.select_operation.operation_list())
            self.send_datagram(datagram_operation)
            self.socket.settimeout(self.socket_timeout)
            datagram_recv = self.socket.recv(self.buffer)
            metadata_json = json.loads(datagram_recv.decode())
            if metadata_json['file_name'] == self.select_operation.operation_list():
                files_name = (base64.b64decode(metadata_json['metadata'])).decode()
                return files_name
            else:
                raise Exception('Datagrams decoding error: inconsistent buffer')
        except Exception as error:
            return('Error: ' + str(error))
    
    # command_get : second command selectable from the Client.
    def command_get(self, file_name):
        if file_name == '':
            return('The file name should be a string (Not Empty)')
        try:
            number_datagrams_received = 0            
            datagram_operation = self.maker_datagram.datagram_operation(file_name, self.select_operation.operation_get())
            self.send_datagram(datagram_operation)
            buffer_rec = self.buffer * 2
            self.socket.settimeout(self.socket_timeout)
            file = open(self.files_path + '/' + file_name, 'wb')
            while True:
                datagram_recv = self.socket.recv(buffer_rec)
                metadata_json = json.loads(datagram_recv.decode())
                if'FILE_END' == metadata_json['file_name']:
                    file.close()
                    break
                elif'ERROR' == metadata_json['file_name']:
                    raise Exception((base64.b64decode(metadata_json['error'])).decode())
                file.write(base64.b64decode(metadata_json['metadata']))
                number_datagrams_received+= 1
                print('Datagram Received: ' + str(number_datagrams_received))
                time.sleep(self.sleep_time)
        except Exception as error:
            os.remove(self.files_path + '/' + file_name)
            return('Error: ' + str(error))
        return (' - ' + file_name + ' => ' + (base64.b64decode(metadata_json['metadata'])).decode())
    
    # command_put : third command selectable from the Client.
    def command_put(self, file_name):
        if file_name == '':
            return('The file name should be a string (Not Empty)')
        try:
            datagram_operation = self.maker_datagram.datagram_operation(file_name, self.select_operation.operation_put())
            self.send_datagram(datagram_operation)
            if os.path.isfile(self.files_path + '/' + file_name):
                number_datagram_sent = 0
                file_length = os.stat(self.files_path + '/' + file_name)
                number_datagram_send = math.ceil(file_length.st_size / self.buffer)
                file_send = open(self.files_path + '/' + file_name, 'rb')
                for i in range(number_datagram_send):
                    metadata = file_send.read(self.buffer)
                    datagram = self.maker_datagram.datagram(file_name, sys.getsizeof(metadata), metadata)
                    self.send_datagram(datagram)
                    number_datagram_sent+= 1
                    print('Datagram Sent: ' + str(number_datagram_sent))
                if number_datagram_sent == number_datagram_send:
                    datagram_end = self.maker_datagram.datagram('FILE_END', 0, 'Sending of file datagrams is over: Upload complete'.encode())
                    self.send_datagram(datagram_end)
                    return(' - ' + file_name + ' => ' + 'Sending of file datagrams is over: Upload complete')
                else:
                    self.send_datagram_error(self.select_operation.operation_put(), 'Error while sending datagrams'.encode())
                    return('Error while sending datagrams')
            else:
                self.send_datagram_error(self.select_operation.operation_put(), 'The file is not present in the Client'.encode())
                return('The file is not present in the Client')
        except Exception as error:
            self.send_datagram_error(self.select_operation.operation_put(), str(error).encode())
            return('Error: ' + str(error))

    # command_close : fourth command selectable from the Client.
    def command_close(self):
        self.socket.close()
        return('Server connection closed.')
        