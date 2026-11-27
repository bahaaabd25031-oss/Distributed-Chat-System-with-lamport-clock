# **Distributed Chat System using lamport clock**  

## server.py

### start_server

first of all it opens a socket with the ip address 127.0.0.1 and TCP port 65000.
then it listens to any connection and when a user connects to it, it opens a thread for each user so multiple users can connect to the same server simultaneously and passes the arguments *conn* & *addr* to the function *"handle_client"* in the thread.
and there is queues for users, current messages and the history of the messages and these queues are thread safe.
also there the ***lock*** object used  to prevent race conditions when accessing shared data.
the used libraries are:

+ socket
+ threading
+ queue
+ json

### handle_client

This function handles each client in a different thread to support multipe users.
first thing it sends the messages history to the newly connected user. then it receives messages from the user in the form of a json file and checks whether the message is empty or not.
It turns the json file into a python dictionary and sets the value of key *"id"* to **USER_ID** which is incremented each time a user is connected.
it breaks from the loop and closes the connection if the message is *"EXIT"* (case insensitive), otherwise it pushes(enqueue) the message to ***messages*** and ***messages_history*** queues.
then it sends the contents of ***messages*** queue to all connected users in json format.
in the end it send the closing message *"close"* and removes the user from the *users* queue by only keeping the other connections.

## client.py

### start_client

first it opens a socket then it connects to the same ip & port numbers stated above.
it creats a thred for receiving messages so it can send and receive at the same time. in the while loop it increments the timestamp (**CLOCK**) which is the lamport clock in this system and asks for users input then it puts it in a dictionary with the timestamp then turns it into json file to send it.
if the message is **"EXIT"** it breaks from the loop and the connection gets closed in the **"receive"** function. another way to close the connection is through KeyboardInterrupt which is handled by using try/except.

### receive

it recives messages from other users through the server and divides them at each newline (\n),
then turns them into json and if the message is **"close"** it closes the connection otherwise
it uses **lock** to change CLOCK  

```python
with lock:
    CLOCK = max(CLOCK, msg_dict["time_stamp"]) + 1
```

and append the messages to a list called **messages** then sort it based on timestamp & id.

```python
messages.append(msg_dict)
messages.sort(key=lambda x: (x["time_stamp"], x["id"]))
```

finally the terminal is cleared by the following code line

```python
os.system('cls' if os.name == 'nt' else 'clear')
```

then the chat is printed in the correct order.

```python
print("--------------Chat--------------")
for msg_dict in messages:
    print(f"[id={msg_dict['id']} | t={msg_dict['time_stamp']}] {msg_dict['message']}")
```
