from __future__ import print_function
import json, struct, traceback
from threading import Lock

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
        print(*args,**kwargs)

def pexc():
    if DEBUG and EXCEPTION:
        traceback.print_exc()

def msg_encode(header = {}, body = b""):
    header = json.dumps(header).encode()
    len_header = len(header)
    len_header = struct.pack("H",len_header)
    len_body = len(body)
    len_body = struct.pack("I",len_body)
    return len_header+len_body+header+body

def msg_decode(msg):
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

def socket_msg_recv(sk):
    try:
        buffer = sk.recv(6)

        header_len = struct.unpack("H",buffer[:2])[0]
        if header_len > 0: buffer += sk.recv(header_len)
        
        body_len = struct.unpack("I",buffer[2:6])[0]
        if body_len > 0:buffer += sk.recv(body_len)
        if len(buffer) > 6:
            return msg_decode(buffer)
        else:
            return {}, b""
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

