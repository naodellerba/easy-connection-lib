from __future__ import unicode_literals, print_function
import json, struct
class InvalidEncoding(Exception): pass
class ConnectionError(Exception):pass
class ListenTimeoutError(Exception):pass
class SendMessageError(Exception):pass

def timeout_func(func, args=(), kwargs={}, timeout_duration=1, default=None):
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
    buffer = sk.recv(6)

    header_len = struct.unpack("H",buffer[:2])[0]
    if header_len > 0: buffer += sk.recv(header_len)
    
    body_len = struct.unpack("I",buffer[2:6])[0]
    if body_len > 0:buffer += sk.recv(body_len)
    if len(buffer) > 6:
        return msg_decode(buffer)
    else:
        return {}, b""

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

