import socket
import threading
import json

HOST = '127.0.0.1'
PORT = 12345
active_clients = []

def listen_for_messages(client, from_username):
    while True:
        try:
            message = client.recv(2048).decode('utf-8')
            temp = json.loads(message)
            if temp['command'] == "users":
                message_dict = {"command":"users", "users":[x[0] for x in active_clients]}
                client.send(json.dumps(message_dict).encode('utf-8'))
                continue
            if message != '':
                to_username = temp['message'].split("~")[0]
                content = temp['message'].split("~")[1]

                final_msg = {"command":"message", "message":from_username + '~' + content}
                for user in active_clients:
                    if user[0]==to_username:
                        send_message_to_client(user[1], json.dumps(final_msg))
                        break
            else:
                print(f"The message send from client {from_username} is empty")
        except Exception as e:
                print(f"Error: {e}")
                client.close()
                active_clients.remove((from_username, client))
                message_dict = {"command":"left", "message":"[SERVER] " + f"{from_username} left the chat"}
                send_messages_to_all(json.dumps(message_dict))
                break

def send_message_to_client(client, message):
    client.send(message.encode('utf-8'))

def send_messages_to_all(message):
    for user in active_clients:
        send_message_to_client(user[1], message)

def client_handler(client):
    while True:
        message = client.recv(2048).decode('utf-8')
        temp = json.loads(message)

        if temp['command'] == "add_client":
            prompt_message = {"command":"message", "message":"SERVER~" + f"{temp['message']} added to the chat"}
            send_messages_to_all(json.dumps(prompt_message))
            active_clients.append((temp['message'], client)) #username, client
            break
        else:
            print("Username is empty")

    threading.Thread(target=listen_for_messages, args=(client, temp['message'], )).start()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
        print(f"Running the server on {HOST} {PORT}")
    except:
        print(f"Unable to bind to host {HOST} and port {PORT}")

    server.listen()

    while True:
        client, address = server.accept()
        print(f"Successfully connected to client {address[0]} {address[1]}")

        threading.Thread(target=client_handler, args=(client,)).start()

if __name__ == '__main__':
    main()