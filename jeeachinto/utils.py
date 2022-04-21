from __future__ import print_function
import json, struct, traceback
from jeeachinto.universal_lock import Lock

class InvalidEncoding(Exception): pass
class ConnectionError(Exception):pass
class ClientNotConnected(Exception):pass
class ListenTimeoutError(Exception):pass
class SendMessageError(Exception):pass

DEBUG = False
EXCEPTION = True
TIMEOUT_SOCKS = 3

def pdbg(*args,**kwargs):
    if DEBUG:
        if not "flush" in kwargs:
            kwargs["flush"] = True
        print(*args,**kwargs)

def pexc():
    if DEBUG and EXCEPTION:
        traceback.print_exc()

def sock_exact_recv(sock,n_bytes):
    data = b""
    while n_bytes > 0:
        packet = sock.recv(n_bytes)
        data+=packet
        n_bytes-=len(packet)
    return data

def msg_encode(header = {}, body = b""):
    header = json.dumps(header).encode()
    len_header = len(header)
    len_header = struct.pack("H",len_header)
    len_body = len(body)
    len_body = struct.pack("I",len_body)
    return len_header+len_body+header+body

def socket_msg_recv(sk):
    while True:
        try:
            header_len = struct.unpack("H",sock_exact_recv(sk, 2))[0]
            body_len = struct.unpack("I",sock_exact_recv(sk, 4))[0]
            header = body = b""
            if header_len > 0: header = sock_exact_recv(sk, header_len)
            if body_len > 0: body = sock_exact_recv(sk, body_len)
            if len(header) + len(body) > 0:
                header = json.loads(header)
                if not "action" in header.keys(): continue
                pdbg("PACKET_BEF_DECODE",header,body)
                return header, body
        except Exception:
            raise ConnectionError()

class ProcessEvent:
    def __locked_lock(self):
        res = Lock()
        res.acquire()
        return res
    
    def __init__(self):
        self.lock = self.__locked_lock()
        self.signallock = Lock()

    def wait(self, blocking = True, timeout=None):
        wait_sess = self.lock
        if timeout is None: locked = wait_sess.acquire(blocking)
        else: locked = wait_sess.acquire(timeout=timeout)
        if locked:
            wait_sess.release()
        return locked
    
    def signal(self):
        self.signallock.acquire()
        prev_lock = self.lock
        self.lock = self.__locked_lock()
        prev_lock.release()
        self.signallock.release()


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

