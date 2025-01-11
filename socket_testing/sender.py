import socket

def start_client(host, port, message):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect to the server at the specified host and port
    client_socket.connect((host, port))
    print(f"Connected to server at {host}:{port}.")

    # Send the message to the server
    client_socket.sendall(message.encode('utf-8'))
    print(f"Sent message: {message}")

    # Close the client socket
    client_socket.close()
    print("Client disconnected.")


if __name__ == "__main__":
    HOST = '127.0.0.1'  # Localhost (same machine)
    PORT = 65432        # Port to connect to
    MESSAGE = "Hello from the client!"
    start_client(HOST, PORT, MESSAGE)

