import socket, threading, queue, json

users = queue.Queue() # thread safe queue for all connected users

messages = queue.Queue() # thread safe queue for current messages

messages_history = queue.Queue() # thread safe queue for the chat history

lock = threading.Lock() # to prevent race conditions

HOST , PORT = '127.0.0.1' , 65000 # ip and port number of the server
        
def handle_client(conn, addr, USER_ID):
    print(f"[NEW] {addr} connected.")
    with conn:
        for msg_dict in messages_history.queue: # send chat history to new user
            conn.sendall((json.dumps(msg_dict) + "\n").encode())
        while True:
            data = conn.recv(1024) # receive message
            if not data:
                break
            msg_dict = json.loads(data.decode())
            msg_dict["id"] = USER_ID
            msg = msg_dict["message"]
            if msg.strip().upper() == 'EXIT': # break from loop
                break
            with lock:
                messages_history.put(msg_dict)
                messages.put(msg_dict) # enqueue to the queues 
                while not messages.empty(): # send current messages to all connected users
                    msg_dict = messages.get()
                    for user in users.queue:
                        user.sendall((json.dumps(msg_dict) + "\n").encode())
            print(f"[{addr}] {msg}")
        msg_dict = {"time_stamp": msg_dict["time_stamp"], "id": USER_ID, "message": "close"}  # end connection
        conn.sendall((json.dumps(msg_dict) + "\n").encode())
        with lock: # remove user (dequeue) 
            for _ in range(users.qsize()):
                temp = users.get()
                if temp != conn:
                    users.put(temp)
    print(f'[closed] {addr}')


def start_server():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # open socket
    s.bind((HOST,PORT))
    s.listen() # listen for connections
    print(f"Listening on {HOST}:{PORT}")
    USER_ID = 0
    while True:
        
        conn, addr = s.accept()
        users.put(conn)
        USER_ID += 1
        threading.Thread(target=handle_client, args=(conn, addr, USER_ID)).start() # start the thread

        
if __name__=='__main__':
    start_server()
