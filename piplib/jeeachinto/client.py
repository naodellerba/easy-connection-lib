from multiprocessing import Lock
import socket
from . import utils

class Client:
    def __init__(self, server_ip, server_port=4545):
        self.server_ip = server_ip
        self.server_port = server_port
        self.name = None
        self.listen_buffer = []
        self.connected = False
        self.readlock = Lock()
        self.writelock = Lock()
        self.socket = None
    
    def __connected_check(self):
        if not self.socket or not self.connected:
            raise utils.ClientNotConnected()

    def send_to_server(self, header = {}, body = b""):
        self.__connected_check()
        self.writelock.acquire()
        try:
            self.socket.sendall(utils.msg_encode(header,body))
        finally:
            self.writelock.release()
    
    def recv_from_server(self):
        self.__connected_check()
        return utils.socket_msg_recv(self.socket)

    def recv_action(self, action = "recv", timeout=None):
        self.__connected_check()
        self.readlock.acquire()
        try:
            for i in range(len(self.listen_buffer)):
                if self.listen_buffer[i][0]["action"] == action:
                    result = self.listen_buffer[i]
                    del self.listen_buffer[i]
                    return result
            self.socket.settimeout(timeout)
            while True:
                msg = self.recv_from_server()
                if msg[0]["action"] == action:
                    return msg
                else:
                    self.listen_buffer.append(msg)
            return result
        except socket.timeout:
            self.close()
            raise utils.ListenTimeoutError()
        finally:
            self.socket.settimeout(utils.TIMEOUT_SOCKS)
            self.readlock.release()


    def connect(self, name=None):
        if self.connected: return
        self.name = name
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(utils.TIMEOUT_SOCKS)
        self.socket.connect((self.server_ip,self.server_port))
        self.connected = True

        try:
            self.send_to_server({"action":"subscribe"} if self.name is None else {"action":"subscribe", "name":self.name})
            header, _ = self.recv_from_server()
        except Exception:
            self.close()
            raise utils.ConnectionError("No answer")

        if header["action"] == "subscribe-status":
            if header["status"] is None:
                self.name = header["name-assigned"]
            else:
                self.close()
                raise utils.ConnectionError(header["status"])
        else:
            self.close()
            raise utils.ConnectionError("Cannot reach the server!")

    def listen(self,timeout=None):
        self.__connected_check()
        header, body = self.recv_action(timeout=None)
        return header["by"], body
    
    def sendto(self, dest_name, body):
        self.__connected_check()
        self.send_to_server({ "action":"send", "to":dest_name },body)
        header, _ = self.recv_action("send-status", timeout=10)
        if not header["status"] is None:
            raise utils.SendMessageError(header["status"])
    
    def close(self):
        if self.connected:
            self.socket.close()
            self.socket = None
            self.connected = False
            self.listen_buffer = []

