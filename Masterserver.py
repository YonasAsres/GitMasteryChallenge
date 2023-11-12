import socket
import os
import multiprocessing
import random

# Define the storage server addresses and weights as dictionaries
storage_servers = [
    {'host': 'localhost', 'tcp_port': 12345, 'udp_port': 12346, 'weight': 2},  # TCP storage server with weight 2
    {'host': 'localhost', 'tcp_port': 12347, 'udp_port': 12348, 'weight': 1}  # UDP storage server with weight 1
]

def load_balance(file_name):
    # Implement weighted load balancing logic
    total_weight = sum(server['weight'] for server in storage_servers)
    random_weight = random.uniform(0, total_weight)

    cumulative_weight = 0
    selected_server = None

    for server in storage_servers:
        cumulative_weight += server['weight']
        if random_weight < cumulative_weight:
            selected_server = server
            break

    return selected_server

def receive_and_forward_tcp(client_socket, client_address):
    try:
        # Receive the protocol identifier (TCP)
        protocol_data = client_socket.recv(4)
        if not protocol_data:
            return
        protocol = protocol_data.decode().lower()

        # Receive the file name
        file_name = client_socket.recv(1024).decode()
        selected_server = load_balance(file_name)

        with open(file_name, 'wb') as file:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                file.write(data)

        client_socket.close()
        print(f"{protocol.upper()} File received from {client_address}: {file_name}")

        # Forward the file to the selected storage server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as storage_socket:
            storage_socket.connect((selected_server['host'], selected_server['tcp_port']))
            with open(file_name, 'rb') as file:
                while True:
                    data = file.read(1024)
                    if not data:
                        break
                    storage_socket.send(data)

        print(f"File '{file_name}' forwarded to storage server at {selected_server['host']}:{selected_server['tcp_port']}")

    except Exception as e:
        print(f"{protocol.upper()} Error: {str(e)}")

def receive_and_forward_udp(server_socket):
    try:
        while True:
            data, client_address = server_socket.recvfrom(1024)
            protocol = data.decode().lower()

            data, _ = server_socket.recvfrom(1024)
            file_name = data.decode()

            with open(file_name, 'wb') as file:
                while True:
                    data, _ = server_socket.recvfrom(1024)
                    if not data:
                        break
                    file.write(data)

            print(f"Received file '{file_name}' on {protocol.upper()} storage server (Port {storage_port})")

    except Exception as e:
        print(f"{protocol.upper()} Storage Server Error: {str(e)}")

def receive_and_forward(client_socket, client_address):
    # Detect the protocol type (TCP/UDP) based on the client_socket type.
    if isinstance(client_socket, socket.socket) and client_socket.type == socket.SOCK_DGRAM:
        # UDP connection
        receive_and_forward_udp(client_socket)
    else:
        # TCP connection
        receive_and_forward_tcp(client_socket, client_address)

def main():
    host = '127.0.0.1'  # Bind to the loopback address (localhost)
    tcp_port = 12349  # Choose an appropriate TCP port for clients
    udp_port = 12350  # Choose an appropriate UDP port for clients

    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        tcp_server_socket.bind((host, tcp_port))
        udp_server_socket.bind((host, udp_port))

        tcp_server_socket.listen(5)  # Listen for incoming TCP connections

        while True:
            print("Waiting for incoming file transfer...")

            tcp_client_socket, tcp_client_address = tcp_server_socket.accept()
            udp_data, udp_client_address = udp_server_socket.recvfrom(1024)

            if udp_data.decode().lower() == 'udp':
                udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                udp_client_socket.bind((host, 0))  # Bind to a random available port
                udp_client_socket.sendto("UDP".encode(), udp_client_address)

                udp_process = multiprocessing.Process(target=receive_and_forward, args=(udp_client_socket, udp_client_address))
                udp_process.start()
            else:
                tcp_process = multiprocessing.Process(target=receive_and_forward, args=(tcp_client_socket, tcp_client_address))
                tcp_process.start()

    except Exception as e:
        print(f"Main Error: {str(e)}")

    finally:
        tcp_server_socket.close()
        udp_server_socket.close()

if __name__ == '__main__':
    main()
