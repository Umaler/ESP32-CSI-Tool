from socket import *

# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Assign IP address and port number to socket
serverSocket.bind(('', 5000))

filename = 'test_2.csv'
packet_count = 3000
count = 0

with open(filename, 'w') as f:
    while True:

        # Receive the client packet along with the address it is coming from
        message, _ = serverSocket.recvfrom(1024)
        string = message.decode()

        print(count, string)
        f.write(string)

        count += 1
        if count >= packet_count:
            break
