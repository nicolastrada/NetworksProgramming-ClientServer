#Elaborato Programmazione ad Oggetti
#Ferri Samuele - Strada Nicola

# Class MakeDatagram:
# This class is used for the construction of the different 'Datagrams' then sent to the Server; using
# the 'MakeDatagaram' class we can define a standard so that the packets sent are always
# defined according to a precise construct.
# All necessary information will be placed in a dictionary, in the defined fields, and then loaded into a
# JSON file as strings.
# The three types of Datagram defined are: 
# I) datagram_operation: Used for communicating the operation chosen by the Client to the Server. 
# II) datagram_error: Used for communicating of a possible error during one of the possible operations that
#                     can be called.
# III) datagram: Used as the standard default packet, where the 'metadata' field will contain the
#                part of the information, encoded in Base64, and the relative size of the sent packet. 

import json
import base64

class MakeDatagram:
    
    # Argument : file_name --> Used for the file name, in the operation of 'get' or 'put', in the operation_list
    #                          this field is setted to void.
    # Argument : operation --> Used for the type of the operation is selected by the Client.
    def datagram_operation(self, file_name, operation):
        datagram_operation = {
                    'file_name' : file_name,
                    'operation' : operation
        }
        return json.dumps(datagram_operation)
    
    # Argument : file_name --> Used for the file name, in the operation where is occured the error.
    # Argument : command --> Used for the type of the operation is selected by the Client, and where was
    #                        generate the error.
    # Argument : error --> Used for the error string generate during the operation, cathed for comunicate with
    #                      the Client.
    def datagram_error(self, file_name, command, error):
        datagram_error = {
                    'file_name': file_name,
                    'command' : command,
                    'error' : base64.b64encode(error).decode('ascii')
        }
        return json.dumps(datagram_error)

    # Argument : file_name --> Used for the file name, in the operation of 'get' or 'put', of the file
    #                          Downloaded from the Server or Uploaded on the Server.
    # Argument : size --> Used for the full size in byte of the Datagram sent.
    # Argument : metadata --> Field that contains the part of data sent or received, this data are encoding in
    #                         Base64 for permits to send every type of file.      
    def datagram(self, file_name, size, metadata):
        datagram = {
                    'file_name' : file_name,
                    'size' : size,
                    'metadata' : base64.b64encode(metadata).decode('ascii')
        }
        return json.dumps(datagram)
