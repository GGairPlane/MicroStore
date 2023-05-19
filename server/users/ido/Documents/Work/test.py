import sqlite3, os, pickle
class UserFileORM:
    def __init__(self):
        self.conn = None  # will store the DB connection
        self.cursor = None   # will store the DB connection cursor

    def open_DB(self):
        """
        will open DB file and put value in:
        self.conn (need DB file name)
        and self.cursor
        """
        self.conn = sqlite3.connect('userfil.db')
        self.current = self.conn.cursor()

    def close_DB(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()
        
        
    def create_table(self, table_name):
        self.open_DB()
        sql = f"""CREATE TABLE {table_name} (
                        file_name text PRIMARY KEY,
                        perms integer
        );"""
        
        self.current.execute(sql)
        self.commit()
        self.close_DB()
        print("assss")
    
    def get_all(self, table_name):
        self.open_DB()
        sql = f"SELECT * FROM {table_name}"
        res = self.current.execute(sql)
        self.commit()
        self.close_DB()
        
    def add_file(self, table_name, file_name, perms):
        self.open_DB()
        sql = f"INSERT INTO {table_name} ({file_name}, {perms})"
        self.current.execute(sql)
        self.commit()
        self.close_DB()



with open(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'users.pickle'), 'wb') as f:
        pickle.dump({}, f)