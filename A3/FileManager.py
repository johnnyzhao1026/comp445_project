'''
COMP 445 lab assignment 2

@ authors: Hualin Bai (40053833), Qichen Liu (40055916)
@ date: 2021-10-23
@ version: 1.0.0
'''
import logging
import os
import re
import threading
class FileOperation:
    '''
    The class is to store different operations of File Manager.
    '''
    Invalid = 0
    GetFileList = 1
    GetFileContent = 2
    GetResource = 3
    PostResource = 4
    PostFileContent = 5
    Download = 6

class FileManager:
    '''
    The class is to manager files in the data directory.
    '''
    lock = threading.Lock()

    def __init__(self):
        # init status is 404 
        self.status = '404'
        self.content = ''
        self.dic_status = {'200':'OK', '301':'Moved Permanently', '404':'Not Found', '400':'Bad Request', \
                            '505':'HTTP Version Not Support'}

    def get_files_list_in_dir(self, dir_path):
        '''
        The method is to get files list in the data directory.
        :param: dir_path
        :return: files list
        '''
        lst_files = []

        for root, dirs, files in os.walk(dir_path):
            for file in files:
                temp = root + '/' + file
                lst_files.append(temp[(len(dir_path) + 1):])
            # lst_files.append(files)
            # ignore __pycache__ dir
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
        # set status
        self.status = '200'
        # print('[Debug] File list : 200')
        return lst_files


    def get_file_content(self, file_name, dir_path):
        '''
        The method is to get file content by filename.
        :param: filename
        :return: fileContent
        '''
        # Secure Access
        file_list, file_name, dir_path = self._check_file_name(file_name, dir_path)
        if len(file_list) > 0:
            # find file
            if file_name in file_list:
                FileManager.lock.acquire()
                try:
                    with open(dir_path + '/' + file_name, 'r', errors="ignore") as f:
                        content = f.read()
                finally:
                    FileManager.lock.release()
                   
                self.status = '200'
                self.content = content

            else:
                # set HTTP 404 Not Found
                self.status = '404'
                self.content = 'File is Not Found'
        else:
            # set HTTP 404 Not Found
            self.status = '404'
            self.content = 'No File exist in the Directory'

        return self.content


    def _check_file_name(self, file_name, dir_path):
        '''
        The method is to check if the file name is valid and has one more paths.
        :param: file_name
        :param: dir_path
        :return: file_list (if length is 0, then invalid file)
        :return: file_name
        :return: dir_path
        '''
        file_list = []
        # Secure Access
        if re.match(r'\.\.\/', file_name):
            self.status = '400'
            self.content = 'Client Cannot Access to read/write any file outside the file server working directory!!!'
            logging.warning(f'Client Cannot Access : {dir_path}')
        elif dir_path != 'data':  
            self.status = '400'
            self.content = 'Not Access - Contact Server Admin to set correct work directory!'
        else:
            # split dir_name and check path, such as 'data/data2/foo2'
            if re.match(r'\/',file_name):
                dir_path = file_name.split('/')[-2]
                file_name = file_name.split('/')[-1]
            # find file
            file_list = self.get_files_list_in_dir(dir_path)
    
        return file_list, file_name, dir_path

    
    def post_file_content(self, file_name, dir_path, content_body):
        '''
        The method is to create/overwrite the file named file_name in dir_path,
        with the content of the body of the request.
        :param: file_name
        :param: dir_path
        :param: content_body
        :return: content of the response
        '''
         # Check Secure Access
        file_list, file_name, dir_path = self._check_file_name(file_name, dir_path)
        
        if len(file_list)>0:
            # TODO: change type formate By Content-Type
            # TODO: Consider Thread Lock
            FileManager.lock.acquire()
            try:
                # creae or overwrite the file named file_name
                with open(dir_path + '/' + file_name, 'w') as f:
                    f.write(content_body)
            except IOError as err:
                self.status = '400'
                self.content = f'Fail to write content into \'{dir_path}/{file_name}\', Error is {err} '
            else:
                # TODO: Consider Thread Lock
                # set status and content of the response
                self.status = '200'
                self.content = f'Success to write content into \'{dir_path}/{file_name}\' '
                FileManager.lock.release()
            
            
        else:
            self.status = '400'
            self.content = f'Fail to write content into \'{dir_path}/{file_name}\', Invalid the path of working directory! '

        return self.content



        