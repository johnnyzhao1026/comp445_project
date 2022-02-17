from httpc import Httpc
import threading
import time

def run(task_cmd,client_name):
    print(f'[Debug] Command is : {task_cmd}, client is : {client_name}')
    Httpc().onecmd(task_cmd)
    time.sleep(3)
    print(f'[Debug] {client_name} : End Task')

if __name__ == '__main__':
    # http://httpbin.org/get?course=networking&assignment=1
# http://httpbin.org/status/418
    task = ["get -v 'http://httpbin.org/get?course=networking&assignment=1'",
    "post -h Content-Type:application/json -d '{\"Assignment\": 1}' http://httpbin.org/post",
    "post -h Content-Type:application/json -d '{\"Assignment\": 3}' http://localhost:8080"
    ]
    client_name = ['Client 1', 'Client 2']

    threadLock = threading.Lock()
    threads = []
    client1 = threading.Thread(target=run, args=(task[1],client_name[0]))
    # client2 = threading.Thread(target=run, args=(task[2],client_name[1]))
    
    # start thread
    client1.start()
    # client2.start()

    threads.append(client1)
    # threads.append(client2)

    # wait all threads finished
    for t in threads:
        t.join()
    print('Exiting Main Thread')



