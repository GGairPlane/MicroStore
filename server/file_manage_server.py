import os
import json
import shutil
import sql_orm


def lsdir(dir):
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
    while os.path.exists(dst):
        dst = os.path.splitext(dst)[0] + "_copy" + os.path.splitext(dst)[1]
    if os.path.exists(src):
        shutil.copy(src, dst)
        return True
    return False


def move(src, dst):
    while os.path.exists(dst):
        dst = os.path.splitext(dst)[0] + "_copy" + os.path.splitext(dst)[1]
    if os.path.exists(src):
        shutil.move(src, dst)
        db = sql_orm.UserFileORM()
        db.delete_file(src)
        return True
    return False


def rename(src, dst):
    if os.path.exists(src):
        os.rename(src, dst)
        db = sql_orm.UserFileORM()
        db.change_name(src, dst)
        return True
    return False


def new_file(path, data):
    if os.path.exists(path):
        return False
    with open(path, "wb") as f:
        f.write(data)
    return True


def new_dir(path):
    if os.path.exists(path):
        return False
    os.mkdir(path)
    return True


def get_file(path):
    if os.path.exists(path) and os.path.isfile(path):
        with open(path, "rb") as f:
            return f.read()
    return None
