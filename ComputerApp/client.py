import socket
import sys
import json
import random
from file_manage_client import *
from tcp_by_size import *
import glbl
import hashlib
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES


def dh(client_sock):
    p = int(recv_by_size(client_sock).decode())
    g = random.randint(1, p - 2)
    send_with_size(client_sock, str(g).encode())
    secret = random.randint(1, g)
    b = pow(g, secret, p)
    a = int(recv_by_size(client_sock).decode())
    send_with_size(client_sock, str(b).encode())

    return str(pow(a, secret, p))


class AESCipher(object):
    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, data):
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))
        return iv + encrypted_data

    def decrypt(self, data):
        iv = data[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(data[AES.block_size :]), AES.block_size)
        return decrypted_data


def logtcp(dir, txt):
    """
    log direction and all TCP byte array data
    return: void
    """
    try:
        if dir == "sent":
            print(f"C LOG:Sent     >>>{txt[:100]}")
        else:
            print(f"C LOG:Recieved <<<{txt[:100]}")
    except:
        print("text unprintable")


def protocol_build_request(cmd, path1=None, path2=None):
    try:
        """
        build the request according to user selection and protocol
        return: string - msg code
        """
        if type(path1) == str:
            path1 = path1.encode()
        if type(path2) == str:
            path2 = path2.encode()

        if cmd == "cd":
            return b"CHGDR~" + path1
        elif cmd == "remove":
            return b"REMOV~" + path1
        elif cmd == "upload":
            return b"UPLOD~"  + upload_file(path1)
        elif cmd == "download":
            return b"DWNLD~" + path1
        elif cmd == "cut":
            return b"MOVFL~" + path1 + b"~" + path2
        elif cmd == "copy":
            return b"COPYP~" + path1 + b"~" + path2
        elif cmd == "rename":
            return b"CHGNM~" + rename(path1)
        elif cmd == "new dir":
            return b"MKDIR~" + makedir(path1)
        elif cmd == "share":
            name, perm = share()
            return b"SHARE~" + name + b"~" + path1 + b"~" + perm
        elif cmd == "getshare":
            return b"GTSHR~"
        elif cmd == "exit":
            return b"EXITT~goodbye"
        elif cmd == "9":
            return path1
        else:
            return b""
    except:
        glbl.sent = True
        return b""


def handle_reply(reply):
    """
    parse the server reply and prepare it to user
    return: answer from server string
    """
    reply_Lst = reply.split(b"~")[:2]
    reply_Lst.append(b"~".join(reply.split(b"~")[2:]))
    reply = reply_Lst
    simplifed = b""
    try:
        if reply[0] == b"RECHD":
            simplifed = json.loads(reply[1].decode())

        elif reply[0] == b"REDWN":
            simplifed = download_file(reply)

        elif reply[0] == b"REGTS":
            simplifed = json.loads(reply[1].decode())

        elif reply[0] == b"ERROR":
            simplifed = "error code: " + reply[1].decode() + " - " + reply[2].decode()
            root = tkinter.Tk()
            root.title("Error")
            canvas1 = tkinter.Canvas(root, width=400, height=100)
            canvas1.create_text(
                200, 50, text=simplifed, fill="black", font=("Helvetica 12 bold")
            )
            canvas1.pack(expand=True, fill=tkinter.BOTH)
            root.mainloop()

    except:
        print("Server replay bad format")
    if simplifed != "":
        print("\n==============")
        try:
            print(f"SERVER Reply: {str(simplifed)}")
        except:
            print("SERVER Reply unprintable")
        print("===============")
    return simplifed


def signin(type, username, password):
    """
    build the signin request
    return: string - msg code
    """
    if type == "l":
        return "LOGIN~" + username + "~" + password

    elif type == "s":
        return "SGNUP~" + username + "~" + password


def main_client(tid, ip):
    global sock
    """
    main client - handle socket and main loop
    """
    connected = False

    sock = socket.socket()
    exit = False
    port = 1233

    try:
        sock.connect((ip, port))
        print(f"Connect succeeded {ip}:{port}")
        key = dh(sock)
        print("key: ", key)
        cipher = AESCipher(key)
        connected = True

    except:
        print(f"Error while trying to connect.  Check ip or port -- {ip}:{port}")
    try:
        if connected:
            logtcp("recv", cipher.decrypt(recv_by_size(sock)))

            while glbl.sent:
                pass
            if glbl.to_send != b"":
                send_with_size(sock, cipher.encrypt(glbl.to_send.encode()))
                logtcp("sent", glbl.to_send)
                glbl.sent = True
                glbl.recieve = cipher.decrypt(recv_by_size(sock))
                glbl.recieved = True
                if b"ERROR" in glbl.recieve:
                    reply_Lst = glbl.recieve.split(b"~")[:2]
                    reply_Lst.append(b"~".join(glbl.recieve.split(b"~")[2:]))
                    reply = reply_Lst

                    # print('Server return an error: ' + glbl.recieve.decode())
                    simplifed = (
                        "error code: " + reply[1].decode() + " - " + reply[2].decode()
                    )
                    root = tkinter.Tk()
                    root.title("Error")
                    canvas1 = tkinter.Canvas(root, width=400, height=100)
                    canvas1.create_text(
                        200,
                        50,
                        text=simplifed,
                        fill="black",
                        font=("Helvetica 12 bold"),
                    )
                    canvas1.pack(expand=True, fill=tkinter.BOTH)
                    root.mainloop()
                    return
            else:
                glbl.sent = True
    except socket.error as err:
        print(f"Got socket error: {err}")

    while connected:
        if tid in glbl.t_die or "all" in glbl.t_die:
            break

        if glbl.to_send == "":
            print("Selection error try again")
            continue
        try:
            if not glbl.sent:
                if glbl.to_send != b"":
                    print("sending:", glbl.to_send[:100])

                    send_with_size(sock, cipher.encrypt(glbl.to_send))

                    logtcp("sent", glbl.to_send)
                    glbl.sent = True
                    recv = cipher.decrypt(recv_by_size(sock))

                    if recv == b"":
                        print("Seems server disconnected abnormal")
                        break
                    logtcp("recv", recv[:100])
                    glbl.recieve = handle_reply(recv)
                    glbl.recieved = True

                    if b"EXITT" in glbl.to_send:
                        print("Will exit ...")
                        connected = False
                        break
                else:
                    glbl.sent = True

        except socket.error as err:
            print(f"Got socket error: {err}")
            break
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as err:
            print(f"General error: {err}")
            break
    print("Bye")
    sock.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_client(sys.argv[1])
    else:
        main_client("127.0.0.1")
