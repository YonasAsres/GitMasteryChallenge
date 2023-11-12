import socket
import threading

# Create a TCP socket for the client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server at a specific host and port
server_address = ("localhost", 8888)  # Change the port to match your server
client_socket.connect(server_address)

# Get the user's chat name
name = input("Enter your chat name: ")

# Send the chat name to the server with the "Login_tag" prefix
client_socket.send(f"Login_tag:{name}".encode())

# Function to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            print(message.decode())
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# Start a thread to receive messages from the server
receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
receive_thread.daemon = True
receive_thread.start()

# Main loop to send messages to the server
while True:
    message = input("Enter message: ")
    if message == "!q":
        break  # Exit the loop and close the client
    client_socket.send(f"{name}:{message}".encode())

# Close the client socket when done
client_socket.close()

