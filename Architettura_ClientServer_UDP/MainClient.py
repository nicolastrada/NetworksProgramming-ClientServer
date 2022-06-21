#Elaborato Programmazione ad Oggetti
#Ferri Samuele - Strada Nicola

from Client.Client import Client
from Operation import Operation

client = Client()
select_operation = Operation()
try:
    client.check_directory('Files_Client')
    while True:
        print('Waiting for the Server connection...')
        print(client.get_home_server())
        command = input('Waiting for the command choice: ')
        if command == select_operation.operation_list():
            print(client.command_list())
        elif command == select_operation.operation_get():
            file_name = input('Insert the file name to download from the Server: ')
            print('Command ' + command + ':')
            print(client.command_get(file_name), end=("\n\n"))
        elif command == select_operation.operation_put():
            print('Files present on the Client:')
            for file_name in client.list_files_client():
                print(' - ' + file_name)
            file_name = input('Insert the file name to upload on the Server: ')
            print('Command ' + command + ':')
            print(client.command_put(file_name), end=("\n\n"))
        elif command == select_operation.operation_close():
            print('Command ' + command + ':')
            print(client.command_close())
            break
        else:
            print('The selected command is unavailable or incomplete! \n')
except Exception as error:
    print(error)
    print(client.command_close())
