import socket
import random
import time

def start_client(host, port):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect to the server at the specified host and port
    client_socket.connect((host, port))
    print(f"Connected to server at {host}:{port}.")

    try:
        for i in range(5):  # Send 5 messages
            message = f"Message {i+1} from the client!"
            # Send the message to the server
            client_socket.sendall(message.encode('utf-8'))
            print(f"Sent: {message}")

            # Wait for a random time between 1 to 3 seconds
            time.sleep(random.randint(1, 3))

    except KeyboardInterrupt:
        print("Client stopped manually.")

    finally:
        # Ensure the socket is closed at the end
        client_socket.close()
        print("Client disconnected.")

if __name__ == "__main__":
    HOST = '127.0.0.1'  # Localhost (same machine)
    PORT = 65432        # Port to connect to
    start_client(HOST, PORT)
