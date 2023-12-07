import socket
import threading
import sys

host = "127.0.0.1"
port = 5555
clients = []
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(5)
server_is_running = True

def broadcast(message, sender_nick=""):
    for client_sock, nick in clients:
        if nick != sender_nick:
            try:
                client_sock.send(f"{sender_nick}: {message}".encode())
            except:
                remove((client_sock, nick))

def send_server_message(message):
    for client_sock, _ in clients:
        try:
            client_sock.send(f"Serwer: {message}".encode())
        except:
            pass

def remove(client):
    if client in clients:
        clients.remove(client)

def handle_client(client_sock, nick):
    while True:
        try:
            message = client_sock.recv(1024).decode()
            if not message:
                break
            if message == "#exit":
                broadcast(f"{nick} opuścił czat.", "Serwer")
                remove((client_sock, nick))
                client_sock.send("#exit".encode())
                client_sock.close()
                break
            print(f"{nick}: {message}")
            if message.startswith("#server "):
                send_server_message(message[len("#server "):])
            else:
                broadcast(message, nick)
        except (socket.error, ConnectionResetError):
            remove((client_sock, nick))
            break

    print(f"{nick} opuścił czat.")
    client_sock.close()

def server_input():
    global server_is_running
    while server_is_running:
        try:
            message = input()
            if message == "#exit":
                print("Zamykanie serwera...")
                server_is_running = False
                broadcast("Serwer zostaje wyłączony. Do zobaczenia!", "Serwer")
                server_socket.close()
                break
            send_server_message(message)
        except Exception as e:
            print(f"Błąd podczas wysyłania wiadomości od serwera: {e}")

print(f"Serwer nasłuchuje na {host}:{port}...")
print("Wpisz wiadomość dla klientów (lub '#exit' aby zamknąć serwer): ")

server_input_thread = threading.Thread(target=server_input)
server_input_thread.start()

while server_is_running:
    try:
        client_sock, addr = server_socket.accept()
        print(f"Nowe połączenie od {addr}")

        nick = client_sock.recv(1024).decode()
        clients.append((client_sock, nick))

        broadcast(f"{nick} dołączył do czatu.", "Serwer")

        client_thread = threading.Thread(target=handle_client, args=(client_sock, nick))
        client_thread.start()
    except (socket.error, KeyboardInterrupt):
        break
