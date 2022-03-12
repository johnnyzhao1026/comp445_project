'''
COMP 445 lab assignment 2

@ authors: Hualin Bai (40053833), Qichen Liu (40055916)
@ date: 2021-10-23
@ version: 1.0.0
'''
import logging
import re
from FileManager import FileOperation

class HttpMethod:
    '''
    The class is to store request method name.
    '''
    Get = "GET"
    Post = "POST"
    Invalid = "Invalid"

class HttpRequestParser:
    '''
    The class is to parser the Http Request from Client.
    '''
    def __init__(self, request):
        '''
        The method is to parser the request from Client.
        :param: request
        '''
        # default values
        self.contentType = "application/json"
        self.operation = ''
        # split header and body of request
        self.http_header, self.http_body = request.split('\r\n\r\n')
        # get method, resource, version 
        header_lines = self.http_header.split('\r\n')
        self.method, self.resource, self.version = header_lines[0].split(' ')
        # get header info and set Content-Type
        self.dict_header_info = {}
        for line in header_lines[1:]:
            if re.match(r'Content-Type', line):
                self.contentType = line.split(':')[1]
            elif re.match(r'Content-Disposition', line):
                self.operation = FileOperation.Download
                if re.match(r'/(.+)', self.resource):
                    # ignore the first '/'
                    self.fileName = self.resource[1:]
            else:
                key, value = line.split(':')
                self.dict_header_info[key] = value
            

        # set operation
        self._set_operation()


    def _set_operation(self):
        '''
        The method is to set the file operation by different request.
        '''
        # GET method
        if self.method == HttpMethod.Get and self.operation != FileOperation.Download:
            # basic GET request
            if re.match(r'/get',self.resource):
                if self.resource in ['/get','/get?']:
                    self.param = ''
                else:
                    # split /get?course=networking&assignment=1
                    temp = self.resource.split('?')[-1]
                    result = {}
                    for item in temp.split('&'):
                        key, value = item.split('=')
                        result[key] = value
                    self.param = result   
                    # print(f'[Debug] Params : \n {result}')
                    logging.debug(f'Params : {result}')
                self.operation = FileOperation.GetResource

            elif self.resource == '/':
                self.operation = FileOperation.GetFileList
            else:
                if re.match(r'/(.+)', self.resource):
                    self.operation = FileOperation.GetFileContent
                    # ignore the first '/'
                    self.fileName = self.resource[1:]
                    # print(f'[Debug] FileName is : {self.fileName}')
                    logging.debug(f'FileName is : {self.fileName}')
                else:
                    self.operation = FileOperation.Invalid

        # POST method
        elif self.method == HttpMethod.Post:
            if self.resource == '/post':
                # set self data of body
                self.data = self.http_body
                self.operation = FileOperation.PostResource

            else:
                if re.match(r'/(.+)',self.resource):
                    # post file
                    self.fileName = self.resource[1:]
                    self.operation = FileOperation.PostFileContent
                    self.data = self.http_body
                else:
                    self.operation = FileOperation.Invalid
        elif self.operation == FileOperation.Download:
            pass
        # Invalid method
        else: 
            self.operation = FileOperation.Invalid

        


        