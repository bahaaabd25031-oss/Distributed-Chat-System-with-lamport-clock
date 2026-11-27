import socket, threading, json, os

HOST, PORT= '127.0.0.1', 65000 # ip and port number of the server

CLOCK = 0 # lamport clock

lock = threading.Lock() # to prevent race conditions

def start_client():
    try:
        global CLOCK
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # open socket
        s.connect((HOST, PORT)) # connect to server
        threading.Thread(target=receive, args=(s,)).start() # stsrt thread ro receive messages
        print('[Write "exit" to quit]')
        while True:
            msg = input() # ask for input
            with lock:
                CLOCK += 1 # increment timestamp 
            msg_dict = {"time_stamp": CLOCK, "id": "", "message": msg}
            msg_json = json.dumps(msg_dict) # turn into json
            s.sendall(msg_json.encode())
            if msg_dict["message"].upper() == "EXIT": # end client
                break
    except KeyboardInterrupt:
        with lock:
            CLOCK += 1
        msg_dict = {"time_stamp": CLOCK, "id": "", "message": "exit"}
        msg_json = json.dumps(msg_dict)
        s.sendall(msg_json.encode())
    except ConnectionRefusedError:
        print('Can not connect to server.')
        s.close()
    finally:
        os.system('cls' if os.name == 'nt' else 'clear') # clear the terminal
        print('EXITED')


def receive(s):
    global CLOCK
    messages = []
    buffer = ""
    while True:
        data = s.recv(1024)
        if not data:
            s.close()
            break
        buffer += data.decode()
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1) # divide messages
            if not line.strip():
                continue
            try:
                msg_dict = json.loads(line) # turn them into dict
            except json.JSONDecodeError:
                continue
            msg = msg_dict["message"]
            if msg.strip().upper() == "CLOSE":
                s.close()
                return
            with lock:
                CLOCK = max(CLOCK, msg_dict["time_stamp"]) + 1 # change timestamp
            messages.append(msg_dict)
            messages.sort(key=lambda x: (x["time_stamp"], x["id"])) # sort them by timestamp first then id
        
        os.system('cls' if os.name == 'nt' else 'clear') # clear terminal
        print("--------------Chat--------------") # print the chat in the correct order
        for msg_dict in messages:
            print(f"[id={msg_dict['id']} | t={msg_dict['time_stamp']}] {msg_dict['message']}")
        
if __name__=="__main__":
    start_client()