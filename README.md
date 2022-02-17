# COMP-445
Data Communications &amp; Computer Networks

### Change Python version in Conda
```zsh
$ conda create -n comp445 python=3.7 anaconda
# after success
$ conda activate comp445
# deactive
$ conda deactivate
```

### Required Environment
- python 3.7

### lists of libaries
- socket
- argparse
- cmd
- sys
- re
- urllib.parse
- shlex
- json

### Usage of Assignment 1
1. `cd` into the folder `A1`
2. run `python httpc.py`
3. follow the prompt (`httpc`), input one of the following test codes
    + GET
        - get 'http://httpbin.org/status/418'
        - get 'http://httpbin.org/get?course=networking&assignment=1'
        - get -v 'http://httpbin.org/get?course=networking&assignment=1'
        - get -h key:value 'http://httpbin.org/get?course=networking&assignment=1'
        - get -h key1:value1 key2:value2 'http://httpbin.org/get?course=networking&assignment=1'
        - get -v 'http://httpbin.org/status/301'
        - (Test redirection : google.com) get -v 'https://bit.ly/3ovMo2i'
        - get -v 'https://bit.ly/3ovMo2i' -o output-google.txt
        - get -v 'http://httpbin.org/get?course=networking&assignment=1' -o output.txt
    + POST
        - post -h Content-Type:application/json -d '{"Assignment": 1}' http://httpbin.org/post
        - post -v -h Content-Type:application/json http://httpbin.org/post
        - post -v -h Content-Type:application/json -d '{"Assignment": 1}' http://httpbin.org/post
        - post -v -h Content-Type:application/json -f test-file.txt http://httpbin.org/post
        - post -v -h Content-Type:application/json -d '{"Test": "Conflict"}' -f test-file.txt http://httpbin.org/post
        - post -v -h Content-Type:application/json http://httpbin.org/post -o output-post.txt
        - post -v 'http://httpbin.org/status/301'
        - post -v http://httpbin.org/status/302
        - (Test rediection 405 Method Not Allowed) post -v 'https://bit.ly/3ovMo2i'
        - post -v -h Content-Type:application/json -d '{"Assignment": 1}' http://httpbin.org/post -o output-post.txt
        
        