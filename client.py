import socket
import threading
import json
import time
 
#group mesaj düzenle

HOST = '127.0.0.1'
PORT = 12345
username = ""
users= []
messages = []
groups = {}

def listen_for_messages_from_server(client):
    global users
    global username
    
    while True:
        message = client.recv(2048).decode('utf-8')
        temp = json.loads(message)

        if temp['command'] == "users":
            users = filter(lambda c: c != username, temp["users"])
            print("Online olanlar: ",','.join(map(str, users)))
        elif temp['command'] == "left":
            print(temp['message'])
            user_temp = temp['message'].split(" ")[1]
            for group_name in groups:
                if(user_temp in groups[group_name]):
                    groups[group_name].remove(user_temp)
            
        elif temp['command'] == "message":
            name = temp['message'].split("~")[0]
            content = temp['message'].split("~")[1]

            if(name == "SERVER"):
                temp = {"command":"users"}
                client.send(json.dumps(temp).encode('utf-8'))
            else:
                messages.append(((name,username),content))
        
            print(f"[{name}] {content}")
        else:
            print("Message reveived from client is empty")

def send_message_to_server(client):
    while True:
        message = input("")
        
        if (message.startswith("/search_message")):
            content = message.split("/search_message ")[1]
            for ((fr,to),cnt) in messages:
                if(content in cnt):
                    print(f"{fr} --> {to} : {cnt}")
            continue
        elif (message.startswith("/search_person")):
            person = message.split("/search_person ")[1]
            for ((fr,to),cnt) in messages:
                if((person == fr) or (person == to)):
                    print(f"{fr} --> {to} : {cnt}")
            continue
        elif (message.startswith("/groups_view")):
            print(list(groups.keys()))
            continue
        elif (message.startswith("/group_view")):
            content = message.split("/group_view ")[1]
            print(groups[content])
            continue
        elif (message.startswith("/group_name_add")):
            group_name = message.split("/group_name_add ")[1]
            groups[group_name]=[]
            continue
        elif (message.startswith("/group_name_remove")):
            group_name = message.split("/group_name_remove ")[1]
            groups.pop(group_name)
            continue
        elif (message.startswith("/group_person_add")):
            group_name = message.split(" ")[1]
            person = message.split(" ")[2]
            groups[group_name].append(person)
            continue
        elif (message.startswith("/group_person_remove")):
            group_name = message.split(" ")[1]
            person = message.split(" ")[2]
            groups[group_name].remove(person)
            continue
        elif (message.startswith("/group_message")):
            group_name = message.split(" ")[1]
            content = message.split(" ")[2]
            group_temp = groups[group_name]
            for person in group_temp:
                temp = {"command":"message", "message":person+"~"+content}
                client.send(json.dumps(temp).encode('utf-8'))
                time.sleep(0.1)
                messages.append(((username, person),content))
            continue
        elif(message.startswith("/")):
            temp = {"command":message.split("/")[1]}
        else:
            temp = {"command":"message", "message":message}
            name = temp['message'].split("~")[0]
            content = temp['message'].split("~")[1]
            messages.append(((username, name),content))
        if message != '':
            client.send(json.dumps(temp).encode('utf-8'))
        else:
            print("Empty message")
            exit(0)

def communicate_to_server(client):
    global username 
    username = input("Enter username: ")
    if username != '':
        temp = {"command":"add_client", "message":username}
        client.send(json.dumps(temp).encode('utf-8'))
    else:
        print("Username cannot be empty")
        exit(0)

    threading.Thread(target=listen_for_messages_from_server, args=(client,)).start()

    send_message_to_server(client)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((HOST, PORT))
        print("Servera basariyla baglanildi")
    except:
        print("Servera baglanilamiyor")

    communicate_to_server(client)

if __name__ == '__main__':
    main()