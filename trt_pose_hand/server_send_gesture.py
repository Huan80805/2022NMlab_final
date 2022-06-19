import socket

HOST = '140.112.18.210'
PORT = 12000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)
print('Gesture sender start at: %s:%s' % (HOST, PORT))

while True:
    print('wait for connection...')
    while True:
        conn, addr = s.accept()
        print('connected by ' + str(addr))
        while True:
            request = conn.recv(1024).decode()
            if request == 'start':
                with open('current_gesture.txt', 'w') as f:
                    f.write('no hand')
                conn.send('Connection confirmed'.encode())
            if request == 'request':
                with open('current_gesture.txt', 'r') as f:
                    response = f.read()
                conn.send(response.encode())
                continue
            if request == 'end':
                break