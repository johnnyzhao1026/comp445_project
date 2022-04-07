'''
COMP 445 lab assignment 1

@ authors: Hualin Bai (40053833), Qichen Liu (40055916)
@ date: 2021-09-20
@ version: 1.0.0
'''
import re
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
        '''
        The method is to return the request for GET.
        :param: request_method : GET or POST
        :return: request_get
        '''
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
            print(f'[Debug] Invalid request method : {request_method}')
            return None

        print(f'[Debug] request is : \n {request}')

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
        rediect_code = ['301','302']
        self.location = ''
        if self.code in rediect_code:
            # get new location path
            for index in range(len(self.header_lines)):
                line_location = re.match(r'Location',self.header_lines[index],re.M|re.I)
                if line_location is not None: 
                    self.location = self.header_lines[index].split(' ')[1]
                    break
            # self.location = self.header_lines[5].split(' ')[1]
            print('[Debug] Rediection Location is : ' + self.location)


        # print(f'[Debug] --- Code --- \n {self.code} \
        #     \n --- header --- \n {self.header} \
        #     \n --- body --- \n {self.body} ')