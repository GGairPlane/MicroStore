import socket
import threading
import time

import pickle
import hashlib, base64
import random
import string

from tcp_by_size import *
from file_manage_server import *
from classes import *
import sql_orm
from gui_classes import *

from Crypto.Util.number import getPrime
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES


all_to_die = False
disconnect_all = False

def dh(cli_sock):
    p = getPrime(30)
    send_with_size(cli_sock, str(p).encode())
    g = int(recv_by_size(cli_sock).decode())
    secret = random.randint(1, g)
    a = pow(g, secret, p)
    send_with_size(cli_sock, str(a).encode())
    b = int(recv_by_size(cli_sock).decode())
    return str(pow(b, secret, p))


class AESCipher(object):
    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, data):
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))
        return iv + encrypted_data

    def decrypt(self, data):
        iv = data[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(data[AES.block_size:]), AES.block_size)
        return decrypted_data



def logtcp(dir, tid, byte_array):
    """
    log direction, tid and all TCP byte array data
    return: void
    """
    if dir == 'sent':
        print(f'{tid} S LOG:Sent     >>> {byte_array[:100]}')
    else:
       print(f'{tid} S LOG:Recieved <<< {byte_array[:100]}')


def signup(request):
    """
    Signup logic
    :param request: b"SGNUP~username~password"
    :return: 
    """
    global users
    request = request.split('~')
    if request[1] in users.keys():
        return b'ERROR~101~Username already exists'
    salt = ''.join(random.choice(string.printable) for i in range(10))
    password = hashlib.sha256(salt.join(request[2]).encode()).hexdigest()
    with threading.Lock():
        users[request[1]] = User(request[1], password, salt)
    
    return b'LOGAK~Signup success'


def login(request):
    """
    Login logic
    :param request: b"LOGIN~username~password"
    :return:
    """
    global users
    request = request.split('~')
    if request[1] not in users.keys():
        return b'ERROR~102~Username does not exists'
    if users[request[1]].connected:
        return b'ERROR~103~User already connected'
    if users[request[1]].password != hashlib.sha256(users[request[1]].salt.join(request[2]).encode()).hexdigest():
        return b'ERROR~111~Password is incorrect'
    return b'LOGAK~Login success'


def protocol_build_reply(request, user):
    """
    Application Business Logic
    function despatcher ! for each code will get to some function that handle specific request
    Handle client request and prepare the reply info
    string:return: reply
    """
   
    request_Lst = request.split(b'~')[:2]
    request_Lst.append(b'~'.join(request.split(b'~')[2:]))
    request = request_Lst
    if len(request[1]) > 0 and  request[1][0] == ord('|'):
        path = db.get_path_by_id(request[1].decode()[1:])
        filename = os.path.split(path)[1].encode()
        perm = db.get_perm(request[1].decode()[1:], user.username)
        reply = b''
        if request[0] == b'CHGDR':      
            if path == b'..':
                user.curr_dir = user.path
                dir  = lsdir(user.path)
            else:
                dir = lsdir(os.path.join(user.path, path.decode()))
                if path.decode() == ".":
                    user.curr_dir = user.curr_dir
                else:            
                    user.curr_dir = os.path.join(user.path, path.decode())
                if dir:
                    reply = b"RECHD~" + dir
                else:
                    reply = "ERROR~201~path does not exists"

        elif request[0] == b'DWNLD':
            file = get_file(path)
            if file:
                reply = b"REDWN~" + filename + b'~' + file
            else:
                reply = "ERROR~201~path does not exists"
        elif request[0] == b'COPYP':
            if copy(os.path.join(user.path, path.decode()), os.path.join(user.path, request[2].decode())):
                reply = b"COPAK~" + filename + b'~' + request[2]
            else:
                reply = "ERROR~202~src path or dst path does not exists"
        elif request[0] == b"GTSHR":
            reply = b"REGTS~" + db.get_all(user.username)
        elif request[0] == b'EXITT':
            reply = 'EXTAK~Goodbye'
            
        if perm == "editor" and reply == b'':
            if request[0] == b'REMOV':
                if remove(path):
                    reply = b"REMAK~" + filename
                else:
                    reply = "ERROR~201~path does not exists"
            elif request[0] == b'UPLOD':
                if new_file(os.path.join(user.curr_dir, path.decode()), request[2]):
                    reply = b"UPLAK~" + path
                else:
                    reply = b'ERROR~203~path already exists' 
            elif request[0] == b'CHGNM':
                if rename(path, os.path.join(os.path.split(path)[0], request[2].decode())):
                    reply = b"CHGAK~" + filename + b'~' + request[2]
                else:
                    reply = "ERROR~201~path does not exists"
            elif request[0] == b'MKDIR':
                if new_dir(os.path.join(user.curr_dir, path.decode())):
                    reply = b"MKDAK~" + path
                else:
                    reply = "ERROR~203~path already exists"
            elif request[0] == b'MOVFL':
                if move(os.path.join(user.path, path.decode()), os.path.join(user.path, request[2].decode())):
                    reply = b"MOVAK~" + filename + b'~' + request[2]
                else:
                    reply = "ERROR~202~src path or dst path does not exists"
            elif request[0] == b'SHARE':
                if db.add_file(path.decode(), os.path.join(user.path, request[2].split(b'~')[0].decode()), request[2].split(b'~')[1].decode()):
                    reply = b"SHRAK~"+path
                else:
                    reply = "ERROR~204~could not share"
        elif reply == b'':
            if request[0] in [b'REMOV', b'UPLOD', b'CHGNM', b'MKDIR', b'MOVFL', b'SHARE']:
                reply = 'ERROR~003~premisison denied'
            else:
                reply = 'ERROR~002~code not supported'

                
        if type(reply) == str:
            return reply.encode()
        return reply
    else:
        if request[0] == b'CHGDR':      
            if request[1] == b'..':
                user.curr_dir = user.path
                dir  = lsdir(user.path)
            else:
                dir = lsdir(os.path.join(user.path, request[1].decode()))
                if request[1].decode() == ".":
                    user.curr_dir = user.curr_dir
                else:            
                    user.curr_dir = os.path.join(user.path, request[1].decode())
                if dir:
                    reply = b"RECHD~" + dir
                else:
                    reply = "ERROR~201~path does not exists"
        elif request[0] == b'REMOV':
            if ".." in request[1].decode() or request[1] == user.curr_dir or request[1] == user.path:
                reply = "ERROR~205~cant delete"
            elif remove(os.path.join(user.curr_dir, request[1].decode())):
                reply = b"REMAK~" + request[1]
            else:
                reply = "ERROR~201~path does not exists"
        elif request[0] == b'UPLOD':
            new_file(os.path.join(user.curr_dir, request[1].decode()), request[2])
            reply = b"UPLAK~" + request[1]
        elif request[0] == b'DWNLD':
            
            file = get_file(os.path.join(user.path, request[1].decode()))
            if file:
                reply = b"REDWN~" + request[1] + b'~' + file
            else:
                reply = "ERROR~201~path does not exists"
        elif request[0] == b'MOVFL':
            if move(os.path.join(user.path, request[1].decode()), os.path.join(user.path, request[2].decode())):
                reply = b"MOVAK~" + request[1] + b'~' + request[2]
            else:
                reply = "ERROR~202~src path or dst path does not exists"
        elif request[0] == b'COPYP':
            if copy(os.path.join(user.path, request[1].decode()), os.path.join(user.path, request[2].decode())):
                reply = b"COPAK~" + request[1] + b'~' + request[2]
            else:
                reply = "ERROR~202~src path or dst path does not exists"
        elif request[0] == b'CHGNM':
            if rename(os.path.join(user.path, request[1].decode()), os.path.join(user.path, request[2].decode())):
                reply = b"CHGAK~" + request[1] + b'~' + request[2]
            else:
                reply = "ERROR~201~path does not exists"
        elif request[0] == b'MKDIR':
            if new_dir(os.path.join(user.curr_dir, request[1].decode())):
                reply = b"MKDAK~" + request[1]
            else:
                reply = "ERROR~203~dir already exists"
                
        elif request[0] == b"SHARE":
            if db.add_file(request[1].decode(), os.path.join(user.path, request[2].split(b'~')[0].decode()), request[2].split(b'~')[1].decode()):
                reply = b"SHRAK~"+request[1]
            else:
                reply = "ERROR~204~could not share"

        elif request[0] == b"GTSHR":
            reply = b"REGTS~" + db.get_all(user.username)
        elif request[0] == b'EXITT':
            reply = 'EXTAK~Goodbye'
        else:
            reply = 'ERROR~002~code not supported'
        if type(reply) == str:
            return reply.encode()
        return reply

def handle_request(request, user):
    """
    Hadle client request
    tuple :return: return message to send to client and bool if to close the client socket
    """
    try:
        to_send = protocol_build_reply(request, user)
        if request[:5] == b'EXITT':
            return to_send, True
    except Exception as e:
        print(e)
        to_send = 'ERROR~001~General error'.encode()
    return to_send, False


def handle_client(sock, tid, addr):
    global users
    """
	Main client thread loop (in the server),
	:param sock: client socket
	:param tid: thread number
	:param addr: client ip + reply port
	:return: void
	"""
    try:
        global all_to_die, disconnect_all
        finish = False
        print(f'New Client number {tid} from {addr}')
        key = dh(sock)
        cipher = AESCipher(key)
        to_send = cipher.encrypt(b"HELLO~welcome to the server")
        send_with_size(sock, to_send)
        logtcp('sent', tid, to_send)
        recv = cipher.decrypt(recv_by_size(sock)).decode()
        logtcp('recv', tid, recv)
        if recv[:5] == "SGNUP":
            ack = signup(recv)
        elif recv[:5] == "LOGIN":
            ack = login(recv)
        send_with_size(sock, cipher.encrypt(ack))
        logtcp('sent', tid, ack)
        if b"ERROR" in ack:
            finish = True
            return


        threading.Lock()
        with threading.Lock():
            user = users[recv.split('~')[1]]
            user.connected = True

        while not finish:
            if all_to_die:
                print('will close due to main server issue')
                break

            byte_data = cipher.decrypt(recv_by_size(sock))
            logtcp('recv', tid, byte_data)
            if byte_data == b'':
                print('Seems client disconnected')
                break
            
            if disconnect_all:
                to_send = b"ERROR~999~all users disconnected"
                finish = True
            else:
                to_send, finish = handle_request(byte_data, user)

            if to_send != b'':
                send_with_size(sock, cipher.encrypt(to_send))
                logtcp('sent', tid, to_send)
            if finish:
                time.sleep(0.1)
                break
            
    except TimeoutError as err:
        print(f'Socket Error exit client loop: err:  {err}')
    except Exception as err:
        print(f'General Error %s exit client loop: {err}')
    with threading.Lock():
        if 'user' in locals() and user.connected:
            user.connected = False
    with open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'users.pickle'), 'wb') as f:
        pickle.dump(users, f)
    print(f'Client {tid} Exit')
    sock.close()




def gui():
    
    global win, clock, all_to_die, disconnect_all, users
    pg.init()
    os.chdir(os.path.split(os.path.realpath(__file__))[0])
    clock = pg.time.Clock()
    win = pg.display.set_mode((1920, 1080))
        
        

    # username = InputBox(890, 500, 200, 32, "username")
    # password = PassBox(890, 650, 200, 32, "password")
    # ip_box = InputBox(245, 262, 250, 32, "127.0.0.1")
    # input_boxes = [username, password, ip_box]

    logout_button = Button((209,225,255), 850, 300, 150,
                          100, 0, "Disconnect all", (0, 0, 0))
    delete_button = Button((209,225,255), 1050, 300,
                        150, 100, 0, "Delete all", (0, 0, 0))
    # join_button = Button((209,225,255), 950, 780, 100, 100, 0, "Join", (209,225,255))
    while not all_to_die:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                all_to_die = True
                return
                        
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if logout_button.rect.collidepoint(event.pos):
                        for user in users.values():
                            user.curr_dir = user.path
                            user.copied = None, 0
                            user.connected = False
                            disconnect_all = True
                            print(user, "disconnected")
                           
                    elif delete_button.rect.collidepoint(event.pos):
                        disconnect_all = True

                        users = {}
                        with open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'users.pickle'), 'wb') as f:
                            pickle.dump(users, f)
                        for dir in os.listdir("users"):
                            shutil.rmtree(os.path.join("users", dir))
                            print(dir, "deleted")
                        if os.path.exists("userfile.db"):
                            os.remove("userfile.db")
                        db.create()
                        
                            
                        
                        
                        
            logout_button.draw(win)
            delete_button.draw(win)
            pg.display.update()
            clock.tick(60)
            
                
    




def main():
    global all_to_die
    global users
    global db
    global disconnect_all
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    db = sql_orm.UserFileORM()
    """
	main server loop
	1. that accept tcp connection
	2. create thread for each connected new client
	3. wait for all threads
	4. every X clients limit will exit
	"""
    threads = []
    srv_sock = socket.socket()
    with open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'users.pickle'), 'rb') as f:
        users = pickle.load(f)

    srv_sock.bind(('0.0.0.0', 1233))

    srv_sock.listen(20)
    print('after listen ... start accepting')

    # next line release the port
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_sock.settimeout(3)
    
    t = threading.Thread(target=gui)
    t.start()
    threads.append(t)
    
    i = 1
    
    print('Main thread: before accepting ...')

    while not all_to_die:
        try:
            cli_sock, addr = srv_sock.accept()
            t = threading.Thread(target=handle_client, args=(cli_sock, str(i), addr))
            t.start()
            i += 1
            threads.append(t)
            if i > 100000000:     # for tests change it to 4
                print('Main thread: going down for maintenance')
                break
        except TimeoutError:
            pass

    all_to_die = True
    print('Main thread: waiting to all clints to die')
    for t in threads:
        t.join()
    srv_sock.close()
    with open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'users.pickle'), 'wb') as f:
        pickle.dump(users, f)
    print('Bye ..')


if __name__ == '__main__':
    main()
