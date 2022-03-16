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

class Httpfs(cmd.Cmd):
    intro = '\nWelcome to httpfs, Type help or ? to list commands. Press ''Ctrl+C'' or Type ''quit'' to terminate.\n'
    prompt = 'httpfs '

    # basic httpfs help menu
    def do_help(self, arg):
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
        print('\033c')

    def do_quit(self, arg):
        print('End of project! Bye!')
        sys.exit(0)
    

    def default(self, cmd):
        # parse the command from console
        parser_server = argparse.ArgumentParser(description='httpfs is a simple file server'
        , conflict_handler = 'resolve')
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
            args = parser_server.parse_args(cmd.split())
            self._run_server('localhost',args.port, args.dir)
        except:
            print('Wrong Information! Please enter again')  
            return


    def _run_server(self, host, port, dir_path):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            ip_addr = socket.gethostbyname(host)
            listener.bind((host, port))
            listener.listen(5)
            print(f'Echo server is listening at {port} ')
            while True:
                conn, addr = listener.accept()
                threading.Thread(target=self._handle_client, args=(conn, addr, dir_path)).start()
        finally:
            listener.close()


    def _handle_client(self, conn, addr, dir_path):
        print(f'\nNew client from {addr}')
        BUFFER_SIZE = 1024
        try:
            data = b''
            while True:
                part_data = conn.recv(BUFFER_SIZE)
                data += part_data
                if len(part_data) < BUFFER_SIZE:
                    break
            client_request = data.decode("utf-8")
            print(f'Client request is :\n{client_request}')
            # Parse Request
            request_parser = HttpRequestParser(client_request)

            server_response = self._get_response(request_parser, dir_path)

            conn.sendall(server_response.encode("utf-8"))
        finally:
            conn.close()
            print(f'\nClient: {addr} is disconnected from Server.')  


    def _get_response(self, request_parser, dir_path):
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
            print(f'files list is : {files_list}')
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

        print(f'Server send Response to client:\n{full_response}')

        return full_response




# main
if __name__ == '__main__':
    try:
        Httpfs().cmdloop()
    except KeyboardInterrupt:
        print('End of project! Bye!')

