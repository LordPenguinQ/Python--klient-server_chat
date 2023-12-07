import socket
import threading

def receive_messages(client_sock):
    while True:
        try:
            message = client_sock.recv(1024).decode()
            if not message:
                break
            if message == "#exit":
                print("Zostałeś wylogowany.")
                break
            print(message)
        except (socket.error, ConnectionResetError):
            break

host = "127.0.0.1"
port = 5555

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((host, port))

nick = input("Podaj swój nickk: ")
client_sock.send(nick.encode())

receive_thread = threading.Thread(target=receive_messages, args=(client_sock,))
receive_thread.start()

print("Wpisz wiadomość (lub '#exit' aby zamknąć serwer): ")

while True:
    message = input()
    client_sock.send(message.encode())
    if message == "#exit":
        break

receive_thread.join()  # czekamy na zakończenie wątku odbierającego wiadomości
client_sock.close()
