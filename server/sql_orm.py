import sqlite3
import json
import uuid
import os


class UserFileORM:
    def __init__(self):
        self.conn = None  # Connection to SQLite3 database
        self.cursor = None  # Cursor to execute SQLite3 commands

    def open_DB(self):
        """
        Opens the SQLite3 database connection and cursor.
        """
        self.conn = sqlite3.connect("userfile.db")
        self.current = self.conn.cursor()

    def close_DB(self):
        """
        Closes the SQLite3 database connection.
        """
        self.conn.close()

    def commit(self):
        """
        Commits any changes made to the SQLite3 database.
        """
        self.conn.commit()

    def create(self):
        """
        Creates the "files" and "shares" tables in the SQLite3 database.
        """
        self.open_DB()
        sql = "CREATE TABLE files (id text PRIMARY KEY, path text NOT NULL); CREATE TABLE shares (user text NOT NULL, id text NOT NULL, perm text NOT NULL);"
        self.current.executescript(sql)

        self.commit()
        self.close_DB()

    def get_all(self, user):
        """
        Retrieves all file records associated with a given user from the SQLite3 database.
        Returns a JSON-encoded list of files.
        """
        self.open_DB()
        sql = f"SELECT shares.id, files.path, shares.perm FROM shares INNER JOIN files ON shares.id=files.id WHERE shares.user='{user}'"
        res = self.current.execute(sql)

        files = []
        for row in res:
            if os.path.isfile(row[1]):
                files.append((os.path.split(row[1])[1], row[2], row[0]))
        self.commit()
        self.close_DB()
        return json.dumps(files).encode()

    def add_file(self, user, path, perm):
        """
        Adds a new file record associated with a given user to the SQLite3 database.
        """
        self.open_DB()
        id = str(uuid.uuid4())
        sql = f"""INSERT INTO files (id, path) SELECT '{id}', '{path}' WHERE NOT EXISTS (SELECT path FROM files WHERE path='{path}');
                   INSERT INTO shares (user, id, perm) SELECT '{user}', id, "{perm}" FROM files WHERE path='{path}';"""

        to_return = True
        try:
            self.current.executescript(sql)
        except Exception as e:
            self.close_DB()
            return False

        self.commit()
        self.close_DB()
        return True

    def delete_file(self, path):
        """
        Deletes a file record from the SQLite3 database.
        """
        self.open_DB()

        sql = f"""DELETE FROM shares WHERE id=(SELECT id FROM files WHERE path='{path}');
                   DELETE FROM files WHERE path='{path}';"""

        try:
            self.current.executescript(sql)
        except Exception as e:
            print(e)
            self.close_DB()
            return False

        self.commit()
        self.close_DB()
        return True

    def change_name(self, old_name, new_name):
        """
        Changes the name of a file record in the SQLite3 database.
        """
        self.open_DB()
        sql = f" UPDATE files SET path='{new_name}' WHERE path='{old_name}'"
        self.current.execute(sql)

        self.commit()
        self.close_DB()

    def get_path_by_id(self, id):
        """
        Retrieves the path of a file record by its id from the SQLite3 database.
        """
        self.open_DB()
        sql = f"SELECT path FROM files WHERE '{id}'=id"
        res = self.current.execute(sql)

        for row in res:
            return row[0]

    def get_perm(self, id, user):
        """
        Retrieves the permissions of a file record by its id and associated user from the SQLite3 database.
        """
        self.open_DB()
        sql = f"SELECT perm FROM shares WHERE '{id}'=id AND '{user}'=user"
        res = self.current.execute(sql)

        for row in res:
            return row[0]
