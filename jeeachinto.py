from multiprocessing import Lock
from pydoc import cli
import socket, json, struct
from threading import Thread
from time import time
from unicodedata import name
import uuid

def timeout(func, args=(), kwargs={}, timeout_duration=1, default=None):
    import signal

    class TimeoutError(Exception):
        pass

    def handler(signum, frame):
        raise TimeoutError()

    # set the timeout handler
    signal.signal(signal.SIGALRM, handler) 
    signal.alarm(timeout_duration)
    try:
        result = func(*args, **kwargs)
    except TimeoutError as exc:
        result = default
    finally:
        signal.alarm(0)

    return result


class InvalidEncoding(Exception): pass

def msg_encode(header:dict = {}, body:bytes = b""):
    header = json.dumps(header).encode()
    len_header = len(header)
    len_header = struct.pack("H",len_header)
    len_body = len(body)
    len_body = struct.pack("I",len_body)
    return len_header+len_body+header+body

def msg_decode(msg:bytes):
    if len(msg) < 6:
        raise InvalidEncoding()
    len_header = struct.unpack("H",msg[:2])[0]
    len_body = struct.unpack("I",msg[2:6])[0]
    if len(msg) != len_header+len_body+6:
        raise InvalidEncoding()
    try:
        return json.loads(msg[6:6+len_header]), msg[6+len_header:]
    except Exception:
        raise InvalidEncoding()



"""

subscribe
{
    "action":"subscribe",
    "name":"pepper1" #Se non esiste, genera random
}

subscribe-status
{
    "action":"subscribe-status",
    "name-assigned":"nomeassegnato"
    "status":null/"Errore grave!"
}

send
{
    "action":"send",
    "to":"nomedestinatario"
}

send-status
{
    "action":"send-status",
    "status":null/"Errore grave!"
}

recv
{
    "action":"recv",
    "by":"nomedestinatario"
}

close
{
    "action":"close"
} // Chiudi socket


"""

class Server:
    def __init__(self,bind_ip="0.0.0.0",bind_port=4545):
        self.clienttable = {}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((bind_ip, bind_port))
            s.listen()
            self.socket = s

    def start(self):
        while True:
            conn, _ = self.socket.accept()
            timeout(self.client_accept_handle, args=(conn,), timeout_duration=10)


    def recv_msg_client(self, client):
        buffer = client.recv(6)
        buffer += client.recv(struct.unpack("H",buffer[:2])[0])
        buffer += client.recv(struct.unpack("I",buffer[2:6])[0])
        return msg_decode(buffer)

    def send_msg_client(self, client_name, header={}, body=b""):
        if client_name in self.clienttable:
            with self.clienttable[client_name]["lock"]:
                self.clienttable[client_name]["conn"].sendall(msg_encode(header,body))

    def send_msg_to_client(self, by, to, body):
        if to in self.clienttable:
            self.send_msg_client(to,{
                "action":"recv",
                "by": by
            },body)
            self.send_msg_client(by,{
                "action":"send-status",
                "status":None
            })
        else:
            self.send_msg_client(by,{
                "action":"send-status",
                "status":"Target name not subscribed!"
            })

    def client_listener(self, client_name):
        conn = self.clienttable[client_name]
        while True:
            try:
                header, data = self.recv_msg_client(conn)
                if header["action"] == "close":
                    conn.close()
                    del self.clienttable[client_name]
                    return
                elif header["action"] == "send":
                    self.send_msg_to_client(client_name, header["to"], data)
            except (InvalidEncoding, KeyError): pass
                    
    def client_accept_handle(self, client):
        header, _ = self.recv_msg_client(client)
        if header["action"] != "subscribe":
            client.close()
            return
        name_pc = None

        if "name" in header:
            name_pc = header["name"]
        else:
            name_pc = uuid.uuid5()
        
        if name_pc in self.clienttable:
            client.sendall(msg_encode(
                {
                    "action": "subscribe-status",
                    "name-assigned": name_pc,
                    "status": "Name already subscribed!"
                }
            ))
        else:
            self.clienttable[name_pc] = {"conn":client, "lock":Lock()}
            Thread(target=self.client_listener, args=(name_pc,)).start()
            client.sendall(msg_encode(
                    {
                        "action": "subscribe-status",
                        "name-assigned": name_pc,
                        "status": None
                    }
            ))





    