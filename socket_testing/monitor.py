import socket

def start_server(host, port):
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to the host and port
    server_socket.bind((host, port))
    
    # Enable the server to accept connections (max 1 connection in the backlog)
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}...")

    # Accept a client connection (this is a blocking call)
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address} established.")

    try:
        while True:
            # Receive data from the client
            data = client_socket.recv(1024)
            if data:
                print(f"Received data: {data.decode('utf-8')}")
            else:
                # If no data is received, the client has closed the connection
                break

    except KeyboardInterrupt:
        print("Server stopped manually.")
    
    finally:
        # Close the client and server sockets
        client_socket.close()
        server_socket.close()
        print("Server shut down.")

if __name__ == "__main__":
    HOST = '127.0.0.1'  # Localhost (same machine)
    PORT = 65432        # Port to bind the server to
    start_server(HOST, PORT)
