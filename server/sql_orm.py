import sqlite3, json, uuid
import os
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
        self.conn = sqlite3.connect('userfile.db')
        self.current = self.conn.cursor()

    def close_DB(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()
    
    
    
    def create(self):
        self.open_DB()
        sql = f"CREATE TABLE files (id text PRIMARY KEY, path text NOT NULL); CREATE TABLE shares (user text NOT NULL, id text NOT NULL, perm text NOT NULL);"
        self.current.executescript(sql)
      
        self.commit()
        self.close_DB()
        
    def create_table(self, table_name):
        self.open_DB()
        sql = f"""CREATE TABLE {table_name} (
                        id text PRIMARY KEY,
                        path text NOT NULL,
                        perms text NOT NULL
        );"""
        
        self.current.execute(sql)
        self.commit()
        self.close_DB()
    
    def get_all(self, user):
        self.open_DB()
        sql = f"SELECT shares.id, files.path, shares.perm FROM shares INNER JOIN files ON shares.id=files.id WHERE shares.user='{user}'"
        res = self.current.execute(sql)
        
        dirs = []
        files = []
        for row in res:
            if os.path.isfile(row[1]):
                files.append((os.path.split(row[1])[1], row[2], row[0]))
            elif os.path.isdir(row[1]):
                dirs.append((os.path.split(row[1])[1], row[2], row[0]))
        self.commit()
        self.close_DB()
        return json.dumps((dirs, files)).encode()
        
    def add_file(self, user, path, perm):
        self.open_DB()
        id = str(uuid.uuid4())
        sql = f"""INSERT INTO files (id, path) SELECT '{id}', '{path}' WHERE NOT EXISTS (SELECT path FROM files WHERE path='{path}');
                    INSERT INTO shares (user, id, perm) SELECT '{user}', id, "{perm}" FROM files WHERE path='{path}';"""

        to_return = True
        try:
            self.current.executescript(sql)
        except Exception as e:
            print(e)
            to_return = False
        self.commit()
        self.close_DB()
        return to_return
    
    def get_path_by_id(self, id):
        self.open_DB()
        sql = f"SELECT path FROM files WHERE '{id}'=id"
        print(sql)
        res = self.current.execute(sql)
        for row in res:
            return row[0]
        
    def get_perm(self, id, user):
        self.open_DB()
        sql = f"SELECT perm FROM shares WHERE '{id}'=id AND '{user}'=user"
        print(sql)
        res = self.current.execute(sql)
        for row in res:
            return row[0]
        
