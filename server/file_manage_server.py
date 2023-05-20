import os
import json
import shutil
import sql_orm


def lsdir(dir):
    """
    List the contents of the given directory.
    Returns a JSON-encoded tuple (directories, files).
    If the directory doesn't exist, return None.
    """
    if os.path.exists(dir):
        dirs = []
        files = []
        for item in os.listdir(dir):
            if os.path.isdir(os.path.join(dir, item)):
                dirs.append(item)
            elif os.path.isfile(os.path.join(dir, item)):
                files.append(item)
        return json.dumps((dirs, files)).encode()
    return None


def remove(path):
    """
    Remove the file or directory at the given path.
    Also delete file reference from database if it's a file.
    Return True if successful, False otherwise.
    """
    if os.path.isfile(path):
        db = sql_orm.UserFileORM()
        db.delete_file(path)
        os.remove(path)
        return True
    elif os.path.isdir(path):
        shutil.rmtree(path)
        return True
    return False


def copy(src, dst):
    """
    Copy file from src to dst.
    If a file with the same name exists at the destination, add '_copy' to the name.
    Return True if successful, False otherwise.
    """
    while os.path.exists(dst):
        dst = os.path.splitext(dst)[0] + "_copy" + os.path.splitext(dst)[1]
    if os.path.exists(src):
        shutil.copy(src, dst)
        return True
    return False


def move(src, dst):
    """
    Move file from src to dst.
    If a file with the same name exists at the destination, add '_copy' to the name.
    Also update the file reference in the database.
    Return True if successful, False otherwise.
    """
    while os.path.exists(dst):
        dst = os.path.splitext(dst)[0] + "_copy" + os.path.splitext(dst)[1]
    if os.path.exists(src):
        shutil.move(src, dst)
        db = sql_orm.UserFileORM()
        db.delete_file(src)
        return True
    return False


def rename(src, dst):
    """
    Rename the file or directory at src to dst.
    Also update the file name in the database if it's a file.
    Return True if successful, False otherwise.
    """
    if os.path.exists(src):
        os.rename(src, dst)
        db = sql_orm.UserFileORM()
        db.change_name(src, dst)
        return True
    return False


def new_file(path, data):
    """
    Create a new file at the given path with the given data.
    Return True if successful, False otherwise (e.g., if a file already exists there).
    """
    if os.path.exists(path):
        return False
    with open(path, "wb") as f:
        f.write(data)
    return True


def new_dir(path):
    """
    Create a new directory at the given path.
    Return True if successful, False otherwise (e.g., if a directory already exists there).
    """
    if os.path.exists(path):
        return False
    os.mkdir(path)
    return True


def get_file(path):
    """
    Get the contents of the file at the given path.
    Return the contents as bytes if successful, None otherwise (e.g., if the path doesn't exist or isn't a file).
    """
    if os.path.exists(path) and os.path.isfile(path):
        with open(path, "rb") as f:
            return f.read()
    return None
