# Define player as a client
# request hand pose classification result from server
import time
import socket
class Client_Player():
    def __init__(self, host='140.112.18.210', port=12000):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
    def get_gesture(self):
        self.socket.send("request".encode())
        gesture = self.socket.recv(1024).decode()
        return gesture
    def init_conn(self):
        self.socket.send("start".encode())
        self.socket.recv(1024)
        print("sending request to server")
    def end_conn(self):
        self.socket.send("end".encode())
        self.socket.close()
        print("ending request")
        
if __name__ == "__main__":
    client = Client_Player()
    client.init_conn()
    count = 0
    while count < 500:
        try:
            gesture = client.get_gesture()
            print(gesture)
        except KeyboardInterrupt:
            break
    client.end_conn()