import os


class User:
    def __init__(self, username, password, salt) -> None:
        self.username = username
        self.password = password
        self.salt = salt
        path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "users")
        path = os.path.join(path, username)
        os.mkdir(path)
        self.path = path
        self.curr_dir = path
        #self.copied = None, 0 # (path, 0 = copy / 1 = move)
        self.connected = False
        

# class File:
#     def __init__(self, owner, path, perm):
#         self.owner = path
#         self.path = owner
#         self.perm = perm
        
    
        
        
        