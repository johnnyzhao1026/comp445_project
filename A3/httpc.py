'''
COMP 445 lab assignment 1

@ authors: Hualin Bai (40053833), Qichen Liu (40055916)
@ date: 2021-09-20
@ version: 2.0.0
'''

import sys
import cmd
import argparse
import re
import socket
from urllib.parse import urlparse
from HttpClient import HttpRequest, HttpResponse
import shlex # ignore the space in quotes " x x"
import logging
# from UdpLibrary import *
from UdpUnit import *
class Httpc(cmd.Cmd):
    """ 
    The HttpcLibrary class is to implement cURL command line with basic functions.
    """ 
    
    title = '''

     **      ** ********** ********** *******    ****** 
    /**     /**/////**/// /////**/// /**////**  **////**
    /**     /**    /**        /**    /**   /** **    // 
    /**********    /**        /**    /******* /**       
    /**//////**    /**        /**    /**////  /**       
    /**     /**    /**        /**    /**      //**    **
    /**     /**    /**        /**    /**       //****** 
    //      //     //         //     //         ////// 

    Welcome to httpc, Type help or ? to list commands.
    Press 'Ctrl+C' or Type 'quit' to terminate.

    '''

    intro = "\033[1;33;40m{}\033[0m".format(title)
    prompt = 'httpc '

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
        

    # basic httpc help menu
    def do_help(self, arg):
        '''
        httpc is a curl-like application but supports HTTP protocol only.
            Usage:
                httpc command [arguments]
            The commands are: 
                get    executes a HTTP GET request and prints the response.
                post   executes a HTTP POST request and prints the resonse.
                help   prints this screen.
        '''
        if not arg or arg == 'help':
            print('\nhttpc is a curl-like application but supports HTTP protocol only.\n' +
            'Usage: \n' + '\t httpc command [arguments]\n'
            + 'The commands are: \n' + 
            '\t get    executes a HTTP GET request and prints the response.\n' +
            '\t post   executes a HTTP POST request and prints the resonse.\n' +
            '\t help   prints this screen.\n')
        elif arg == 'get':
            print('\nusage: httpc get [-v] [-h key:value] URL\n' +
            'Get executes a HTTP GET request for a given URL.\n' +
            '\t -v Prints the detail of the response such as protocol, status, and headers.\n' +
            '\t -h key:value Associates headers to HTTP Request with the format \'key:value\'.\n')
        elif arg == 'post':
            print('\nusage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL\n' +
            'Post executes a HTTP POST request for a given URL with inline data or from file.\n' +
            '\t -v Prints the detail of the response such as protocol, status, and headers.\n' +
            '\t -h key:value Associates headers to HTTP Request with the format \'key:value\'.\n' +
            '\t -d string Associates an inline data to the body HTTP POST request.\n' +
            '\t -f file Associates the content of a file to the body HTTP POST request\n' +
            'Either [-d] or [-f] can be used but not both.\n')
        else:
            print('Please input a valid command!!! Type help or ? to get help!!!')
        # return super().do_help(arg)

    def do_clear(self,arg):
        '''
        The method is to clear the screen.
        '''
        print('\033c')

    def do_quit(self,arg):
        '''
        The method is to quit the app.
        '''
        print('Thanks for using! Bye!')
        sys.exit(0)

    def do_get(self, cmd):
        '''
        The method is to execute a HTTP GET request for a given URL.
        :param: cmd : command from console
        :test: get 'http://httpbin.org/status/418'
        :test: get 'http://httpbin.org/get?course=networking&assignment=1'
        :test: get -v 'http://httpbin.org/get?course=networking&assignment=1'
        :test: get -h key:value 'http://httpbin.org/get?course=networking&assignment=1'
        :test: get -h key1:value1 key2:value2 'http://httpbin.org/get?course=networking&assignment=1'
        :test Redirection: get -v 'http://httpbin.org/status/301'
        :test -o filename: get -v 'http://httpbin.org/get?course=networking&assignment=1' -o output.txt
        '''
        # if not cmd: self.do_help('get')
        
        # parse the command from console
        parser_get = argparse.ArgumentParser(description='Get executes a HTTP GET request for a given URL.'
        , conflict_handler = 'resolve') # conflict_handle is to solve the conflict issue of help argument.
        parser_get.prog = 'httpc get'
        parser_get.usage = parser_get.prog + ' [-v] [-h key:value] URL'
        # add optional argument
        parser_get.add_argument('-v','--verbose',help='Prints the detail of the response such as protocol, status, and headers.', action='store_true' )
        parser_get.add_argument('-h','--header',help='Associates headers to HTTP request with the format \'key:value\' ', nargs='+' )

        # add positional argument URL, fix bug : the no expect argument : URL 
        parser_get.add_argument('url',help='a valid http url',default=cmd.split()[-1] ,nargs='?' )
        # print(cmd.split()[-1])
        # print(cmd.split()[:-1])
        # print("[Debug] cmd.split() is : " + str(cmd.split()) )

        # add optional argument -o filename
        parser_get.add_argument('-o','--output',help='write the body of the response to the specific file')

        # assign the valid arguments
        # :test: get -v 'http://httpbin.org/get?course=networking&assignment=1' -o output.txt
        if self._is_valid_url(cmd.split()[-1]):
            args = parser_get.parse_args(cmd.split()[:-1])
        else:
            args = parser_get.parse_args(cmd.split()[:-3] + cmd.split()[-2:] )
            # print('[Debug] split args are : ' + str(cmd.split()[:-3]) + str(cmd.split()[-2:]))
            args.url = cmd.split()[-3]
        
        # print parser help
        # parser_get.print_help()
        print("[Debug] args are : " + str(args) )
        # print(args.url)

        # set logging config
        self._config_logging(args.verbose)
        
        # Check the URL is valid
        if self._is_valid_url(args.url):
            # recall HttpClient to send Http request
        
            # urlparse 
            url_parsed = URL_PARSE(args.url)
            
            # check whether code is 3xx or not
            code_redirect = ['301','302']
            
            while True:    
                # get request  
                request = self._get_request(url_parsed,args,'GET')
                
                # use socket to connect server, get response
                response_content = self._client_socket_connect_server(request)
                # print Output in the console depends on diffenrent requirements (-v)
                self._print_details_by_verbose(args.verbose,response_content)
                # check whether code is 3xx or not
                if response_content.code in code_redirect :
                    # change path and re-parse url
                    if self._is_valid_url(response_content.location):
                        args.url = "'" + response_content.location + "'"
                        url_parsed = URL_PARSE(args.url)
                    else:
                        url_parsed.path = response_content.location
                    print('[Rediection] \'GET\' new location is : ' + response_content.location )        
                else:
                    print('\n[Debug] --- End ---\n')
                    break
            
            # if -o, write to output.txt
            if args.output:
                self._output_file(args, response_content)

    
    # some private methods
    def _is_valid_url(self, url):
        '''
        The method is to check if the url is valid or not.
        :param: url
        :return: boolean
        '''
        # if no quote starts with url, then add it. 
        if url.startswith('\''):
            pass
        else:
            url = '\'' + url + '\''
        # use eval() to omit the ' ' 
        if re.match(r'^https?:/{2}\w.+$',eval(url)):
            # print('[Debug] valid url : ' + url)
            return True
        else: 
            print('[Debug] invalid url')
            return False 

    def _is_valid_header(self, header):
        '''
        The method is to check if the header is valid or not.
        :param: header
        :return: boolean
        '''
        # case considers one more key:value
        if len(header) >= 1:
            # check whether header is valid one by one
            for i in range(len(header)):
                if re.match(r'(.+:.+)',header[i]):
                    print('[Debug] valid header : ' + header[i])
                else: 
                    print('[Debug] invalid header : ' + header[i])
                    return False
        else:
            print('[Debug] no header ')
            return False
        return True

    def _get_request(self, url_parsed, args, request_method):
        '''
        The method is to get request by parsed URL, headers, and request method.
        :param: url_parsed
        :param: args : need args.header, args.data, args.file
        :param: request_method : GET or POST
        :return: request
        '''
        if args.header and self._is_valid_header(args.header):
            # case: one more key:value headers
            headers = ''
            for i in range(len(args.header)):
                headers += args.header[i] + '\r\n'
            if request_method == 'GET':
                request = HttpRequest(url_parsed.hostname, url_parsed.path, url_parsed.query, headers)
            else:
                # POST query means infos of (-d) data or (-f) file
                if args.data and args.file:
                    # data and file cannot be used together
                    print('[Error] Either [-d] or [-f] can be used but not both.')
                    sys.exit(0)
                elif args.data and not args.file:
                    request = HttpRequest(url_parsed.hostname, url_parsed.path, args.data, headers)
                elif not args.data and args.file:
                    # TODO: get the info of files
                    with open(args.file,'r') as f:
                        # read() all infos
                        file_info = f.read()
                    request = HttpRequest(url_parsed.hostname, url_parsed.path, file_info, headers)
                else:
                    request = HttpRequest(url_parsed.hostname, url_parsed.path, '', headers)
        else:
            if request_method == 'GET':
                request = HttpRequest(url_parsed.hostname, url_parsed.path, url_parsed.query,)  
            else: 
                # POST query means infos of (-d) data or (-f) file
                if args.data and args.file:
                    # data and file cannot be used together
                    print('[Error] Either [-d] or [-f] can be used but not both.')
                    sys.exit(0)
                if args.data and not args.file :
                    request = HttpRequest(url_parsed.hostname, url_parsed.path, args.data,)
                elif not args.data and args.file :
                    # TODO: get the info of files
                    with open(args.file,'r') as f:
                        # read() all infos
                        file_info = f.read()
                    request = HttpRequest(url_parsed.hostname, url_parsed.path, file_info, )
                else:
                    request = HttpRequest(url_parsed.hostname, url_parsed.path, '', )
        # get request
        request = request.get_request(request_method)

        return request

    def _client_socket_connect_server(self, request):
        '''
        The method is to connect server using client socket.
        :param: client_udp
        :param: request
        :return: response_content
        '''
        try:
            # Implement UDP
            # client_udp = UdpLibrary()
            client_udp = UdpUnit()
            while True:
                if client_udp.connect_server():
                    # send request
                    logging.debug(f'request is type {type(request)}')
                    break
                # consider miss client request, need resend
                
                # pkt = client_udp.pkt_builder.build(PACKET_TYPE_DATA, 0, request.encode("utf-8"))
                # client_udp.conn.sendto(pkt.to_bytes(), client_udp.router_addr) 
                
                # client send response
                
            while True:
                
                if client_udp.client_send_request(request):
                
                    # receive response
                    data = client_udp.recv_msg()
                    if data is None:
                        logging.debug('Client did not receive response')
                        print('[Debug] Client did not receive response')
                        sys.exit(0)
                    # decode data, and then parse content
                    response_content = HttpResponse(data)
                    
                    client_udp.close_connect()
                    return response_content
                # else:
                #     while True:
                #         client_udp.connect_server()
            # else:
            #     logging.debug('Client Fail to send response to server')
        
            # else:
            #     logging.debug('Fail to connect to server.')
            #     sys.exit(0)
            
        except Exception as e:
            logging.debug('Error: {}'.format(e))
            
        
        

        
        # use socket to connect server, socket.SOCK_STREAM is for TCP
        # client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # try:
        #     client_socket.connect(url_parsed.address)
        #     print('--- Connect success ---')
        #     # get response : data (Type: bytes) that need to be decoded by UTF-8 
        #     data = b''
        #     BUFF_SIZE = 1024
        #     while True:
        #         # send data
        #         client_socket.sendall(request.encode("utf-8"))
        #         # receive data
        #         # MSG_WAITALL waits for full request or error

        #         # response = client_socket.recv(len(request), socket.MSG_WAITALL)
        #         # if response:
        #         #     data += response
        #         # else: break

        #         # instead of above method to FIX BrokenPipe [Error 32], since client closed before recv all response.
        #         response = client_socket.recv(BUFF_SIZE)
        #         data += response
        #         if len(response) < BUFF_SIZE:
        #             break
                
        #     # decode data, and then parse content
        #     response_content = HttpResponse(data)

        # finally:  
        #     # test Broken Pipe Error 32    
        #     client_socket.close()
        #     return response_content
        
    def _print_details_by_verbose(self,args_verbose, response_content):
        '''
        The method is to show different output depends on verbose.
        :param: args_verbose
        :param: response_content
        :return: None
        '''
        # Output depends on diffenrent requirements (-v)
        if args_verbose:
            print('--- Details ---')
            print(response_content.content)
        # other cases
        else: 
            # only print the content.body
            print(response_content.body)

    def _output_file(self, args, response_content):
        '''
        The method is to write the body of the response to the specified file.
        :param: args
        :param: response
        '''
        with open(args.output, 'w') as f:
            f.write(response_content.body)
        print(f'[Output] write the body of the response to the {args.output}')

    def do_post(self,cmd):
        '''
        The method is to executes a HTTP POST request for a given URL with inline data or from file.
        :param: cmd : command from console
        :test: httpc post -h Content-Type:application/json -d '{"Assignment": 1}' http://httpbin.org/post
        :test: httpc post -v -h Content-Type:application/json http://httpbin.org/post
        :test: httpc post -v -h Content-Type:application/json -d '{"Assignment": 1}' http://httpbin.org/post
        :test: httpc post -v -h Content-Type:application/json -f test-file.txt http://httpbin.org/post
        :test: httpc post -v -h Content-Type:application/json -d '{"Test": "Conflict"}' -f test-file.txt http://httpbin.org/post
        :test -o filename: post -v -h Content-Type:application/json http://httpbin.org/post -o output.txt
        :test -o filename: post -v -h Content-Type:application/json -d '{"Assignment": 1}' http://httpbin.org/post -o output.txt
        '''
        # parse the command from console
        parser_post = argparse.ArgumentParser(description='Post executes a HTTP POST request for a given URL with inline data or from file.'
        , conflict_handler = 'resolve') # conflict_handle is to solve the conflict issue of help argument.
        parser_post.prog = 'httpc post'
        parser_post.usage = parser_post.prog + ' [-v] [-h key:value] [-d inline-data] [-f file] URL'
        parser_post.epilog = 'Either [-d] or [-f] can be used but not both. '
        # add arguments   
        parser_post.add_argument('-v','--verbose',help='Prints the detail of the response such as protocol, status, and headers.', action='store_true' )
        parser_post.add_argument('-h', '--header', help='Associates headers to HTTP request with the format \'key:value\' ', nargs='+')
        # add_mutually_exclusive_group
        parser_post.add_mutually_exclusive_group()
        parser_post.add_argument('-d','--data',help='Associates an inline data to the body HTTP POST request.')
        parser_post.add_argument('-f','--file',help='Associates the content of a file to the body HTTP POST request.')
        # add position argument URL, default is to make sure the last argument is URL, add \' for eval() function
        parser_post.add_argument('url',help='a valid http url',default= "'" + shlex.split(cmd)[-1] + "'" ,nargs='?' )
        
        # add optional argument -o filename
        parser_post.add_argument('-o','--output',help='write the body of the response to the specific file')

        # assign the valid arguments
        # :test: post -v -h Content-Type:application/json http://httpbin.org/post -o output.txt
        if self._is_valid_url(shlex.split(cmd)[-1]):
            # shlex is to ignore the space in quotes " x x"
            args = parser_post.parse_args(shlex.split(cmd)[:-1])
        else:
            args = parser_post.parse_args(shlex.split(cmd)[:-3] + shlex.split(cmd)[-2:] )
            # print('[Debug] split args are : ' + str(shlex.split(cmd)[:-3]) + str(shlex.split(cmd)[-2:]))
            args.url = "'" + shlex.split(cmd)[-3] + "'"

        # print('[Debug] args is : ' + str(shlex.split(cmd) ))

        print("[Debug] args are : " + str(args) )
        # test
        # parser_post.print_help()
        
        # set logging config
        self._config_logging(args.verbose)
        
        
        # Check the URL is valid
        if self._is_valid_url(args.url):
            # recall HttpClient to send Http request
        
            # urlparse 
            url_parsed = URL_PARSE(args.url)

            # check whether code is 3xx or not
            code_redirect = ['301','302']
            
            while True:
                # get request  
                request = self._get_request(url_parsed,args,'POST')
                # Implement UDP
                
                # use socket to connect server, get response
                response_content = self._client_socket_connect_server(request)
                # print Output in the console depends on diffenrent requirements (-v)
                self._print_details_by_verbose(args.verbose,response_content)
                # check whether code is 3xx or not
                if response_content.code in code_redirect :
                    # change path
                    # change path and re-parse url
                    if self._is_valid_url(response_content.location):
                        args.url = "'" + response_content.location + "'"
                        url_parsed = URL_PARSE(args.url)
                    else:
                        url_parsed.path = response_content.location
                    
                    print('[Rediection] \'POST\' new location is : ' + response_content.location )
                else:
                    # other code cases
                    print('\n[Debug] --- End ---\n')
                    break               

            if args.output:
                # if -o filename, write to the specified file
                self._output_file(args, response_content)
                
        

class URL_PARSE:
    '''
    The class is to parse the url and store the parameters of url_parsed.
    :params: url, scheme, hostname, port, ip_address, resource, address
    '''
    def __init__(self, args_url):
        # urlparse 
        self.url = eval(args_url)
        self.url = urlparse(self.url)
        self._assign_param_url()

    def _assign_param_url(self):
        '''
        The method is to assign parameters of URL.
        '''
        # assign parameters of url
        self.scheme = self.url.scheme
        self.hostname = self.url.hostname
        self.path = self.url.path
        self.query = self.url.query
        # the standard HTTP TCP port is 80, A2 uses 8080 default
        self.port = 80 if not self.url.port else self.url.port
        print(f'[Debug] Port is : {self.port}')
        self.ip_address = socket.gethostbyname(self.hostname)
        self.resource = self.path
        if self.url.query:
            self.resource += '?' + self.query
        # for socket address
        self.address = (self.ip_address, self.port)


# main
if __name__ == '__main__':
    try:
        Httpc().cmdloop()
    except KeyboardInterrupt:
        print('Thanks for using! Bye!')
