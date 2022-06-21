#Elaborato Programmazione ad Oggetti
#Ferri Samuele - Strada Nicola

# Class Operation:
# This class is used to define a standard for the 4 available operations that can be performed,
# this avoids repetition and inconsistency problems, because every reference to one 
# of the operations will be executed with this class.
# --> operation_home ('home'): Defines the operation in which the Server is requested to send the "home page"
# --> operation_list ('list'): Defines the operation in which the Server is requested to send the list 
#                              complete list of all files on the Server.
# --> operation_get ('get'): Defines the operation in which, with the file name, the Server start the 
#                            Download operation.
# --> operation_put ('put'): Defines the operation in which, with the name of the file, the Server is 
#                            ready to start Upload operation.
# --> operation_close ('close'): Defines the operation in which the Client closes communication with the Server.

class Operation:
    __op_home = 'home'
    __op_list = 'list'
    __op_get = 'get'
    __op_put = 'put'
    __op_close = 'close'
    
    def operation_home(self):
        return self.__op_home
    
    def operation_list(self):
        return self.__op_list
    
    def operation_get(self):
        return self.__op_get
    
    def operation_put(self):
        return self.__op_put
    
    def operation_close(self):
        return self.__op_close
    