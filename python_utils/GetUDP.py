from socket import *

# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Assign IP address and port number to socket
serverSocket.bind(('', 5000))

while True:

    # Receive the client packet along with the address it is coming from
    message, _ = serverSocket.recvfrom(1024)

    print(message.decode())
