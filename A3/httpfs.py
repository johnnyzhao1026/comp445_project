'''
COMP 445 lab assignment 2

@ authors: Hualin Bai (40053833), Qichen Liu (40055916)
@ date: 2021-10-18
@ version: 1.0.0
'''

import sys
import cmd
import argparse
import re
import json
import socket
import threading
import logging
from HttpServer import HttpMethod, HttpRequestParser
from FileManager import FileOperation, FileManager

# from UdpLibrary import *
from UdpUnit import *

class Httpfs(cmd.Cmd):
    """ 
    The Httpfs class is to implement a simple file server.
    """ 

    title = '''

    █████   █████  █████     █████                 ██████         
   ░░███   ░░███  ░░███     ░░███                 ███░░███        
    ░███    ░███  ███████   ███████   ████████   ░███ ░░░   █████ 
    ░███████████ ░░░███░   ░░░███░   ░░███░░███ ███████    ███░░  
    ░███░░░░░███   ░███      ░███     ░███ ░███░░░███░    ░░█████ 
    ░███    ░███   ░███ ███  ░███ ███ ░███ ░███  ░███      ░░░░███
    █████   █████  ░░█████   ░░█████  ░███████   █████     ██████ 
    ░░░░░   ░░░░░    ░░░░░     ░░░░░  ░███░░░   ░░░░░     ░░░░░░  
                                      ░███                        
                                      █████                       
                                      ░░░░░                        

    Welcome to httpfs, Type help or ? to list commands.
    Press 'Ctrl+C' or Type 'quit' to terminate.
    '''
    intro = "\033[1;32;40m{}\033[0m".format(title)
    prompt = 'httpfs '

    # basic httpfs help menu
    def do_help(self, arg):
        '''
        httpfs is a simple file server.

        usage: httpfs [-v] [-p PORT] [-d PATH-TO-DIR]
            -v  Prints debugging messages.
            -p  Specifies the port number that the server will listen and serve at.
                Default is 8080.
            -d  Specifies the directory that the server will use to read/write
                requested files. Default is the current directory when launching the
                application.
        '''
        if not arg or arg == 'help':
            print('''
httpfs is a simple file server.

usage: httpfs [-v] [-p PORT] [-d PATH-TO-DIR]
    -v  Prints debugging messages.
    -p  Specifies the port number that the server will listen and serve at.
        Default is 8080.
    -d  Specifies the directory that the server will use to read/write
        requested files. Default is the current directory when launching the
        application. 
            
            ''')
    
    def do_clear(self, arg):
        '''
        The method is to clear the screen.
        '''
        print('\033c')

    def do_quit(self, arg):
        '''
        The method is to quit the app.
        '''
        print('Thanks for using! Bye!')
        sys.exit(0)

    def _config_logging(self, verbose):
        '''
        The method is to config logging.
        :param: verbose
        :return: logger
        '''
        FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
        if verbose:
            logging.basicConfig(format=FORMAT, datefmt='%Y/%m/%d %H:%M:%S', stream=sys.stdout, level=logging.DEBUG)
        else:
            logging.basicConfig(format=FORMAT, datefmt='%Y/%m/%d %H:%M:%S', stream=sys.stdout, level=logging.INFO)
        

    def emptyline(self):
        '''
        The override method is to use default arguments that -v: False, -p PORT: 8080 and -d PATH-TO-DIR: current dir,
        while typing emptyline.
        '''
        # parse the command from console
        parser_server = argparse.ArgumentParser(description='httpfs is a simple file server'
        , conflict_handler = 'resolve') # conflict_handle is to solve the conflict issue of help argument.
        parser_server.prog = 'httpfs'
        parser_server.usage = parser_server.prog + ' [-v] [-p PORT] [-d PATH-TO-DIR]'
        # add optional argument
        parser_server.add_argument('-v','--verbose',help='Prints debugging messages', action='store_true' )
        parser_server.add_argument('-p','--port',help='Specifies the port number that the server will listen and serve at.\n \
                                    Default is 8080.', type=int, default=8080 )
        parser_server.add_argument('-d','--dir',help='Specifies the directory that the server will use to read/write \
                                    requested files.', default='data' )
        # check if the format of Https is correct
        try:
            # assign args
            args = parser_server.parse_args()
            # print(f'[Debug] verbose is : {args.verbose}, port is : {args.port}, path-to-dir is : {args.dir}')
            
            # set logging config
            self._config_logging(args.verbose)
            logging.debug(f'verbose is : {args.verbose}, port is : {args.port}, path-to-dir is : {args.dir}')
            
            # run http file server
            # self._run_server('localhost',args.port, args.dir)
            self._run_server_udp(args.dir)
        except:
            print('[HELP] Please Enter help to check correct usgae!')  
            return
    

    def default(self, cmd):
        '''
        The method is to Override default fuction to check if the format of Httpfs is correct. 
        :param: cmd : command from console
        '''
        # parse the command from console
        parser_server = argparse.ArgumentParser(description='httpfs is a simple file server'
        , conflict_handler = 'resolve') # conflict_handle is to solve the conflict issue of help argument.
        parser_server.prog = 'httpfs'
        parser_server.usage = parser_server.prog + ' [-v] [-p PORT] [-d PATH-TO-DIR]'
        # add optional argument
        parser_server.add_argument('-v','--verbose',help='Prints debugging messages', action='store_true' )
        parser_server.add_argument('-p','--port',help='Specifies the port number that the server will listen and serve at.\n \
                                    Default is 8080.', type=int, default=8080 )
        parser_server.add_argument('-d','--dir',help='Specifies the directory that the server will use to read/write \
                                    requested files.', default='data' )
        # print("[Debug] cmd.split() is : " + str(cmd.split()) )
        
        # check if the format of Https is correct
        try:
            # assign args
            args = parser_server.parse_args(cmd.split())
            # print(f'[Debug] verbose is : {args.verbose}, port is : {args.port}, path-to-dir is : {args.dir}')
            # print('\n[News] Running the Http file server ...\n')

            # set logging config
            self._config_logging(args.verbose)
            logging.debug(f'verbose is : {args.verbose}, port is : {args.port}, path-to-dir is : {args.dir}')
            logging.info(f'[News] Running the Http file server ...')
            # run http file server
            # self._run_server('localhost',args.port, args.dir)
            self._run_server_udp(args.dir)
        except Exception as e:
            print(f'[Error] {e}') 
            return

    def _run_server_udp(self, dir_path):
        '''
        The method is to implement UDP in A3
        '''
        # UDP
        # server_udp = UdpUnit()
        # server_udp.run_server()
        
        while True:
            # server_udp = UdpLibrary()
            server_udp = UdpUnit()
            server_udp.run_server()
            
            # mimic TCP 3-way handshaking
            if server_udp.connect_client():
                
                # if client_request is not None:
                client_request = None
                while client_request is None:
                    client_request = server_udp.server_response()
                    if client_request is not None:
                        logging.debug(f'Received Client request is :\n{client_request}')
                        # Parse Request
                        request_parser = HttpRequestParser(client_request.decode("utf-8"))
                        server_response = self._get_response(request_parser, dir_path)
                        # send msg
                        server_udp.send_msg(server_response.encode("utf-8"))
                    logging.debug('try to receiving request...')
                            
          
                    
                
        
           
    
    
    def _run_server(self, host, port, dir_path):
        '''
        The method is to run a simple file server by socket.
        :param: args
        '''
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            ip_addr = socket.gethostbyname(host)
            # print(f'[Debug] hostname is : {ip_addr}')
            logging.debug(f'hostname is : {ip_addr}')
            listener.bind((host, port))
            listener.listen(5)
            # print('Echo server is listening at', port)
            logging.info(f'Echo server is listening at {port} ')
            while True:
                conn, addr = listener.accept()
                threading.Thread(target=self._handle_client, args=(conn, addr, dir_path)).start()
        finally:
            listener.close()

    def _handle_client(self, conn, addr, dir_path):
        # print(f'\n[Debug] New client from {addr}')
        logging.debug(f'New client from {addr}')
        BUFFER_SIZE = 1024
        try:
            data = b''
            while True:
                part_data = conn.recv(BUFFER_SIZE)
                data += part_data
                if len(part_data) < BUFFER_SIZE:
                    break
            client_request = data.decode("utf-8")
            # print(f'\n[Debug] --- Receiving Request of Client --- \n\n {client_request} \n\n [Debug] --- End --- \n ')
            logging.debug(f'Client request is :\n{client_request}')
            # test response
            # response = "HTTP1.0/ 200 OK\r\nContext-Type : txt\r\n\r\nServer send response to Client!!!".encode("utf-8")
            # print(f'[Debug] Send Response to Client : \n {response}')

            # Parse Request
            request_parser = HttpRequestParser(client_request)

            server_response = self._get_response(request_parser, dir_path)

            conn.sendall(server_response.encode("utf-8"))
        finally:
            conn.close()
            # print(f'[Debug] Client: {addr} is disconnected from Server.')
            logging.debug(f'Client: {addr} is disconnected from Server.')  

    def _get_response(self, request_parser, dir_path):
        '''
        The method is to get response by request_parser and dir_path.
        :param: request_parser : HttpRequestParser Obj
        :param: dir_path
        :return: response
        '''

        # A file manager
        file_manager = FileManager()
        response = "HTTP1.0/ 404 Not Found\r\nContext-Type: application/json\r\n\r\nNo Response"
        # GET request

        # Basic GET
        if request_parser.operation == FileOperation.GetResource:
            response = self._generate_full_response_by_type(request_parser, request_parser.param, file_manager)
        # GET file list
        elif request_parser.operation == FileOperation.GetFileList:    
            # return a list of current files in the data directory
            files_list = file_manager.get_files_list_in_dir(dir_path)
            # print(f'[Debug] files list is : {files_list}')
            logging.debug(f'files list is : {files_list}')
            # json_file = json.dumps(files_list, ensure_ascii=False)
            # print(f'JSON files is : \n{json_file}')
            response = self._generate_full_response_by_type(request_parser,files_list,file_manager)
        # Get File Content
        elif request_parser.operation == FileOperation.GetFileContent:
            file_content = file_manager.get_file_content(request_parser.fileName, dir_path)
            response = self._generate_full_response_by_type(request_parser, file_content, file_manager)
        # Get Download
        elif request_parser.operation == FileOperation.Download:
            file_content = "Save me!"
            response = self._generate_full_response_by_type(request_parser, file_content, file_manager)
        # Post Resource
        elif request_parser.operation == FileOperation.PostResource:
            response = self._generate_full_response_by_type(request_parser, request_parser.data, file_manager)

        # Post /bar
        elif request_parser.operation == FileOperation.PostFileContent:
            content_response = file_manager.post_file_content(request_parser.fileName, dir_path, request_parser.data)
            response = self._generate_full_response_by_type(request_parser, content_response, file_manager)
        # operation is invalid
        else:
            response = self._generate_full_response_by_type(request_parser, 'Invalid Request', file_manager)

        return response
    

    def _generate_full_response_by_type(self, request_parser, response_body, file_manager):
        '''
        The method is to generate full response by different type formate,
        according to the Content-Type of Header of the request.
        :param: request_parser
        :param: response_body
        :param: file_manager
        :return: response
        '''
        # default return JSON format of response body
        body_output = {}
        # GET Methods
        if request_parser.operation == FileOperation.GetResource:
            body_output['args'] = request_parser.param
            file_manager.status = '200'
        elif request_parser.operation == FileOperation.GetFileList:
            body_output['files'] = response_body
        elif request_parser.operation == FileOperation.GetFileContent:
            if file_manager.status in ['400','404']:
                body_output['Error'] = response_body
            else:
                body_output['content'] = response_body
        # Download
        elif request_parser.operation == FileOperation.Download:
            file_manager.status = '200'
            body_output['Download Info'] = response_body
        # POST methods
        elif request_parser.operation == FileOperation.PostResource:
            body_output['data'] = response_body
        elif request_parser.operation == FileOperation.PostFileContent:
            if file_manager.status in ['400','404']:
                body_output['Error'] = response_body
            else:
                body_output['Info'] = response_body
        # Check Http Version
        elif request_parser.version != 'HTTP/1.0':
            # 505 : HTTP Version Not Support
            file_manager.status == '505'
        else:
            body_output['Invalid'] = response_body
            # file_manager.status = '400'
        # set header info
        body_output['headers'] = request_parser.dict_header_info
        # set json format
        content = json.dumps(body_output)

        response_header = request_parser.version + ' ' + file_manager.status + ' ' + \
            file_manager.dic_status[file_manager.status] + '\r\n' + \
            'Content-Length: ' + str(len(content)) + '\r\n' + \
            'Content-Type: ' + request_parser.contentType + '\r\n'
        # Content-Disposition
        if request_parser.operation == FileOperation.Download:
            response_header += f'Content-Disposition: attachment; filename={request_parser.fileName} \r\n'
        response_header += 'Connection: close' + '\r\n\r\n'
        full_response = response_header + content

        logging.debug(f'Server send Response to client:\n{full_response}')

        return full_response




# main
if __name__ == '__main__':
    try:
        Httpfs().cmdloop()
    except KeyboardInterrupt:
        print('Thanks for using Httpfs! Bye!')

