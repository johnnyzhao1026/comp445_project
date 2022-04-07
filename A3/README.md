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
- logging

### list files:
- httpc.py
- HttpClient.py
- httpfs.py
- HttpServer.py
- FileManager.py
- config.py
- packet.py
- SlidingWindow.py
- UdpUnit.py
- [router]
    - router (Need to Install Go)
- [data]
   - bar
   - foo

### Usage of Assignment 3
1. Step 1: Run the router on the same or different host
   - See the router's README
   ### Test cases
   - run `./router`
   - run ` ./router --drop-rate=0.5 --seed=3 `
   - run ` ./router --drop-rate=0.5 --seed=1 ` (case: client request is dropped)
   - run ` ./router --max-delay=5ms --seed=0 `
   - run ` ./router --drop-rate=0.2 --max-delay=2ms --seed=1 `
   - run ` ./router --drop-rate=0.5 --max-delay=1ms --seed=1 `

2. Step 2: Run the server
   run `python httpfs.py`, follow the prompt (`httpfs`), input one of the following test codes:
    - `httpfs` ( empty line uses default parameters)
    - `httpfs -v`
    - `httpfs -v -p 8080`
    - `httpfs -v -p 8080 -d data`

3. Step 3: Run the client
   run `python httpc.py`, follow the prompt (`httpc`), input one of the following test codes:
   - **NOTE** You need to send your msg when `httpfs` is listening port instead of **TimeOut**
## Some Test Cases of HttpClient
### Get File Manager : read content of a file and listing files
- get -v 'http://localhost:8080/'
- get -v 'http://localhost:8080/foo' (Server uses default dir `data`)

### Post File Manager : create a new file
- post -v -h Content-Type:application/json -d '{"Assignment": 3}, {"Test":"post"}' http://localhost:8080/bar

