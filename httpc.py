

import sys
import cmd
import argparse
import re
import socket
from urllib.parse import urlparse
from HttpClient import HttpRequest, HttpResponse
import shlex # ignore the space in quotes " x x"

class Httpc(cmd.Cmd):    
    title = '''
    Welcome to httpClient, Type help or ? to list commands.
    Press 'Ctrl+C' or Type 'quit' to terminate.
    '''

    intro = '\nWelcome to httpc, Type help or ? to list commands. Press ''Ctrl+C'' or Type ''quit'' to terminate.\n'
    prompt = 'httpc '


    def do_help(self, arg):
        if not arg or arg == 'help':
            print('\nhttpc is a curl-like application but supports HTTP protocol only.\n' +
            'Usage: \n' + '\t httpc command [arguments]\n'
            + 'The commands are: \n' + 
            '\t get    executes a HTTP GET request and prints the response.\n' +
            '\t post   executes a HTTP POST request and prints the resonse.\n' +
            '\t help   prints this screen.\n\n' +
            'Use "httpc help [command]" for more information about a command.\n')
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
    def do_clear(self,arg):
        '''
        The method is to clear the screen.
        '''
        print('\033c')
    def do_quit(self,arg):
        print('Program Exit!')
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
        # parse the command from console
        parser_get = argparse.ArgumentParser(description='Get executes a HTTP GET request for a given URL.', conflict_handler = 'resolve') # conflict_handle is to solve the conflict issue of help argument.
        parser_get.prog = 'httpc get'
        parser_get.usage = parser_get.prog + ' [-v] [-h key:value] URL'
        # add optional argument
        parser_get.add_argument('-v','--verbose',help='Prints the detail of the response such as protocol, status, and headers.', action='store_true' )
        parser_get.add_argument('-h','--header',help='Associates headers to HTTP request with the format \'key:value\' ', nargs='+' )

        # add positional argument URL, fix bug : the no expect argument : URL 
        parser_get.add_argument('url',help='a valid http url',default=cmd.split()[-1] ,nargs='?' )

        # add optional argument -o filename
        # parser_get.add_argument('-o','--output',help='write the body of the response to the specific file')

        # assign the valid arguments
        # if self._is_valid_url(cmd.split()[-1]):
        args = parser_get.parse_args(cmd.split()[:-1])
        # else:
        #     args = parser_get.parse_args(cmd.split()[:-3] + cmd.split()[-2:] )
        #     args.url = cmd.split()[-3]

        # Check the URL is valid
        # if self._is_valid_url(args.url):
        # recall HttpClient to send Http request
    
        # urlparse 
        url_parsed = URL_PARSE(args.url)
        
        # check whether code is 3xx or not
        # code_redirect = ['301','302']
        # while True:    
            # get request  
        request = self._get_request(url_parsed,args,'GET')
            # use socket to connect server, get response
        response_content = self._client_socket_connect_server(url_parsed,request)
            # print Output in the console depends on diffenrent requirements (-v)
        self._print_details_by_verbose(args.verbose,response_content)

    
    # some private methods
    # def _is_valid_url(self, url):
    #     '''
    #     The method is to check if the url is valid or not.
    #     :param: url
    #     :return: boolean
    #     '''
    #     # if no quote starts with url, then add it. 
    #     if url.startswith('\''):
    #         pass
    #     else:
    #         url = '\'' + url + '\''
    #     # use eval() to omit the ' ' 
    #     if re.match(r'^https?:/{2}\w.+$',eval(url)):
    #         # print('[Debug] valid url : ' + url)
    #         return True
    #     else: 
    #         # print('[Debug] invalid url')
    #         return False 

    # def _is_valid_header(self, header):
    #     '''
    #     The method is to check if the header is valid or not.
    #     :param: header
    #     :return: boolean
    #     '''
    #     # case considers one more key:value
    #     if len(header) >= 1:
    #         # check whether header is valid one by one
    #         for i in range(len(header)):
    #             if re.match(r'(.+:.+)',header[i]):
    #                 print('[Debug] valid header : ' + header[i])
    #             else: 
    #                 print('[Debug] invalid header : ' + header[i])
    #                 return False
    #     else:
    #         print('[Debug] no header ')
    #         return False
    #     return True

    def _get_request(self, url_parsed, args, request_method):
        if args.header:
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
                    print('Error ---> -d and -f cannot be used at same time.')
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
                    print('Error ---> -d and -f cannot be used at same time.')
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

    def _client_socket_connect_server(self, url_parsed, request):
        '''
        The method is to connect server using client socket.
        :param: url_parsed
        :param: request
        :param: args
        :return: response_content
        '''
        # use socket to connect server, socket.SOCK_STREAM is for TCP
        client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            client_socket.connect(url_parsed.address)
            # print('--- Connect success ---')
            # get response : data (Type: bytes) that need to be decoded by UTF-8 
            data = b''
            BUFF_SIZE = 1024
            while True:
                # send data
                client_socket.sendall(request.encode("utf-8"))
                # receive data
                # MSG_WAITALL waits for full request or error

                # response = client_socket.recv(len(request), socket.MSG_WAITALL)
                # if response:
                #     data += response
                # else: break

                # instead of above method to FIX BrokenPipe [Error 32], since client closed before recv all response.
                response = client_socket.recv(BUFF_SIZE)
                data += response
                if len(response) < BUFF_SIZE:
                    break
                
            # decode data, and then parse content
            response_content = HttpResponse(data)

        finally:  
            # test Broken Pipe Error 32    
            client_socket.close()
            
            return response_content
        
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
            print(response_content.header)
            print(response_content.body)
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
        # parser_post.add_argument('-o','--output',help='write the body of the response to the specific file')

        # assign the valid arguments
        # :test: post -v -h Content-Type:application/json http://httpbin.org/post -o output.txt
        # if self._is_valid_url(shlex.split(cmd)[-1]):
            # shlex is to ignore the space in quotes " x x"
        args = parser_post.parse_args(shlex.split(cmd)[:-1])
        # else:
        #     args = parser_post.parse_args(shlex.split(cmd)[:-3] + shlex.split(cmd)[-2:] )
        #     # print('[Debug] split args are : ' + str(shlex.split(cmd)[:-3]) + str(shlex.split(cmd)[-2:]))
        #     args.url = "'" + shlex.split(cmd)[-3] + "'"

        # print('[Debug] args is : ' + str(shlex.split(cmd) ))

        # print("[Debug] args are : " + str(args) )
        # test
        # parser_post.print_help()
        
        # Check the URL is valid
        # if self._is_valid_url(args.url):
        # recall HttpClient to send Http request
    
        # urlparse 
        url_parsed = URL_PARSE(args.url)

        # check whether code is 3xx or not
        # bonus marks : supports redirect
        # code_redirect = ['301','302']
        # while True:
        # get request  
        request = self._get_request(url_parsed,args,'POST')
        # use socket to connect server, get response
        response_content = self._client_socket_connect_server(url_parsed,request)
        # print Output in the console depends on diffenrent requirements (-v)
        self._print_details_by_verbose(args.verbose,response_content)



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
        # assign parameters of url
        self.scheme = self.url.scheme
        self.hostname = self.url.hostname
        self.path = self.url.path
        self.query = self.url.query
        # the standard HTTP TCP port is 80, A2 uses 8080 default
        self.port = 80 if not self.url.port else self.url.port
        # print(f'[Debug] Port is : {self.port}')
        self.ip_address = socket.gethostbyname(self.hostname)
        self.resource = self.path
        if self.url.query:
            self.resource += '?' + self.query
        # for socket address
        self.address = (self.ip_address, self.port)


class HttpRequest:
    '''
    The class is to deal with the request of Get and Post.

    '''
    def __init__(self, host, path, query, headers = 'User-Agent: Concordia-HTTP/1.0\r\n'):
        '''
        The method is to initial the request.
        :param: host : hostname
        :param: path : '/get' or '/post'
        :param: query : GET is like as 'course=networking&assignment=1', POST is like '{"Assignment:1"}'
        :param: headers : 'key:value' (eg. 'User-Agent':'Concordia-HTTP/1.0')
        '''
        self.host = host
        self.path = path
        self.query = query
        # default headers
        self.headers = 'User-Agent: Concordia-HTTP/1.0\r\n'
        if self.headers == headers: pass
        else:
            # fix post bug : delete the '\r\n'
            self.headers += headers 
        # resource is combined with the path and query 
        self.resource = self.path 
        if self.query:
            self.resource += '?' + self.query

    def get_request(self, request_method):
        if request_method == 'GET':
            request = ('GET ' + self.resource + ' HTTP/1.0\r\n' + \
                    self.headers + \
                    'Host: ' + self.host + '\r\n\r\n')
        elif request_method == 'POST':
            # HTTP POST Request
            # get content length from the body (query) exists
            content_length = str(len(self.query))
            # POST query means infos of (-d) data or (-f) file (Body data)    
            request = ('POST ' + self.path + ' HTTP/1.0\r\n' + \
                    self.headers \
                    + 'Content-Length: ' + content_length + '\r\n' \
                    + 'Host: ' + self.host + '\r\n\r\n'
                    # + 'Connection: close\r\n\r\n'
                    ) 
            # add Body Http Post request, use query directly instead of json methods
            request += self.query

            # print(f'[Debug] request is : \n {request}')
            # print('[Debug] Post query is : ' + self.query + '\n[Debug] Length is : ' + str(len(self.query)))
        else:
            return None

        return request


class HttpResponse:
    '''
    The class is to parse and split the response from server.
    '''

    def __init__(self,response):
        '''
        The method is to initial the response.
        :param: response
        '''
        # use errors = "ignore" to solve the UnicodeError that cannot decode 'utf-8'
        self.content = response.decode('utf-8', errors="ignore" )
        self.parseContent()

    def parseContent(self):
        '''
        The method is to parse the content.
        '''   
        content = self.content.split('\r\n\r\n')
        self.header = content[0]
        self.body = content[1]
        # get status code: 200 or 3xx, etc
        self.header_lines = self.header.split('\r\n')
        self.header_info = self.header_lines[0].split(' ')
        self.code = self.header_info[1]

        # rediection code (numbers starts with 3xx) 
        # includes 300 Multiple Choices, 301 Moved Permanently, 302 Moved Temporarily, 304 Not Modified
        # rediect_code = ['301','302']
        # self.location = ''
        # if self.code in rediect_code:
        #     # get new location path
        #     for index in range(len(self.header_lines)):
        #         line_location = re.match(r'Location',self.header_lines[index],re.M|re.I)
        #         if line_location is not None: 
        #             self.location = self.header_lines[index].split(' ')[1]
        #             break
        #     # self.location = self.header_lines[5].split(' ')[1]
        #     print('[Debug] Rediection Location is : ' + self.location)


if __name__ == '__main__':
    try:
        Httpc().cmdloop()
    except KeyboardInterrupt:
        print('Thanks for using! Bye!')