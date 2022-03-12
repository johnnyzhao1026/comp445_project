### Required Environment
- python 3.7

### lists of libaries
- socket
- argparse
- cmd
- sys
- re
- urllib.parse
- json
- threading

### list files:
- httpc.py
- HttpClient.py
- httpfs.py
- HttpServer.py
- FileManager.py

### Usage of Assignment 2
1. `cd` into the folder `A2`
2. run `python httpfs.py`, follow the prompt (`httpfs`), input one of the following test codes:
    - `httpfs` ( empty line uses default parameters)
    - `httpfs -v -p 8080`
    - `httpfs -v -p 8080 -d data`
3. add new terminal, `cd` into the folder `A1`, run `python httpc.py`, follow the prompt (`httpc`), input one of the following test codes:
    ### Basic Get
    - get -v 'http://localhost:8080/get?course=networking&assignment=1'
    - get -v -h key1:value1 'http://localhost:8080/get?course=networking&assignment=1'

    ### Get File Manager
    - get 'http://localhost:8080/'
    - get -v 'http://localhost:8080/'
    - get -v 'http://localhost:8080/foo' (Server uses default dir `data`)
    - get -v 'http://localhost:8080/data2/foo2' (Server uses default dir `data`)
    - get -v 'http://localhost:8080/README.md' (Test Secure Access: Server uses `.` as dir_path)
    - get -v 'http://localhost:8080/../README.md' (Test Secure Access: Server uses default dir `data`)

    ### Post File Manager
    - post -h Content-Type:application/json -d '{"Assignment": 2}' http://localhost:8080/bar
    - post -h Content-Type:application/json -f test-file.txt http://localhost:8080/data2/bar2
    #### Test: Invalid woring directory
    - post -h Content-Type:application/json -d '{"Assignment": 2}' http://localhost:8080/../bbb
    #### Test: File Not Found Error, even through in valid working directory.
    - post -h Content-Type:application/json -d '{"Assignment": 2}' http://localhost:8080/data3/bbb
    ### Get different Content Type
    - get -h Content-Type:application/json 'http://localhost:8080/'
    
    ### Content-Disposition
    - get -v -h Content-Disposition:inline 'http://localhost:8080/download'
    