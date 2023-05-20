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
        self.connected = False
        

    
        
        
        