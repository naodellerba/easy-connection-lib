from multiprocessing import Lock
import socket, struct
from . import utils

class Client:
    def __init__(self,server_ip,server_port=4545):
        self.server_ip = server_ip
        self.server_port = server_port
        self.name = None
        self.listen_buffer = []
        self.readlock = Lock()
        self.writelock = Lock()
    
    def send_to_server(self, header = {}, body = b""):
        with self.writelock:
            self.socket.sendall(utils.msg_encode(header,body))
    
    def recv_from_server(self):
        buffer = self.socket.recv(6)
        buffer += self.socket.recv(struct.unpack("H",buffer[:2])[0])
        buffer += self.socket.recv(struct.unpack("I",buffer[2:6])[0])
        return utils.msg_decode(buffer)

    def connect(self, name=None):
        self.name = name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_ip,self.server_port))
        self.send_to_server({"action":"subscribe"} if self.name is None else {"action":"subscribe", "name":self.name})
        header, _ = self.recv_from_server()
        if header["action"] == "subscribe-status":
            if header["status"] is None:
                self.name = header["name-assigned"]
            else:
                raise utils.ConnectionError(header["status"])
        else:
            raise utils.ConnectionError("Cannot reach the server!")

    def listen(self, action = "recv", timeout=None):
        with self.readlock:
            def func():
                for i in range(len(self.listen_buffer)):
                    if self.listen_buffer[i][0]["action"] == action:
                        result = self.listen_buffer[i]
                        del self.listen_buffer[i]
                        return result  
                while True:
                    msg = self.recv_from_server()
                    if msg[0]["action"] == action:
                        return msg
                    else:
                        self.listen_buffer.append(msg)
            if timeout is None:
                result = func()
            else:
                result = utils.timeout_func(func, timeout_duration=timeout)
            if result is None:
                raise utils.ListenTimeoutError()
            else:
                return result
    
    def sendto(self, dest_name, body):
        self.send_to_server({ "action":"send", "to":dest_name },body)
        header, _ = self.listen("send-status", timeout=10)
        if not header["status"] is None:
            raise utils.SendMessageError(header["status"])
    
    def close(self):
        self.send_to_server({ "action":"close" })
        self.socket.close()
        self.socket = None
        self.listen_buffer = None

