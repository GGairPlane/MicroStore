import os
import tkinter
from tkinter import filedialog
import glbl


def upload_file(path):
    """
    Function to upload file to server.

    Args:
        path (str): The path where the uploaded file should be saved.

    Returns:
        to_return (bytes): The path and content of the file to be uploaded.
    """
    glbl.sent = True

    tkinter.Tk().withdraw()

    with filedialog.askopenfile(mode="rb") as f:
        data = f.read()
        file_name = os.path.join(path, os.path.basename(f.name).encode())
    try:
        to_return = file_name + b"~" + data
    except Exception as e:
        print(f"error opening file: {e}")

    glbl.sent = False
    return to_return


def download_file(reply):
    """
    Function to download file from server.

    Args:
        reply (bytes): The server's response containing file name and data.

    Returns:
        str: The file name if downloaded successfully; otherwise error message.
    """
    try:
        tkinter.Tk().withdraw()

        with filedialog.asksaveasfile(
            mode="wb", initialfile=os.path.basename(reply[1].decode())
        ) as f:
            f.write(reply[2])
        return reply[1].decode() + " downloaded"
    except Exception as e:
        return f"file did not download error: {e}"


def rename(old_name):
    """
    Function to rename the file or directory.

    Args:
        old_name (bytes): The original name of the file or directory.

    Returns:
        bytes: The old and new path of the file or directory.
    """
    old_name = old_name.decode()
    name = os.path.split(old_name)[1]
    root = tkinter.Tk()
    root.title("Rename")
    canvas1 = tkinter.Canvas(root, width=400, height=300)
    canvas1.pack()
    entry1 = tkinter.Entry(root)
    entry1.insert(tkinter.END, name)
    entry1.pack()
    canvas1.create_window(200, 140, window=entry1)

    def new_name():
        nonlocal name
        name = entry1.get()
        root.destroy()

    button1 = tkinter.Button(text="Rename", command=new_name)
    canvas1.create_window(200, 180, window=button1)
    root.mainloop()
    name = name.replace("~", "")
    return (
        old_name.encode()
        + b"~"
        + os.path.join(os.path.split(old_name)[0], name).encode()
    )


def makedir(path):
    """
    Function to create a new directory.

    Args:
        path (bytes): The path where the new directory should be created.

    Returns:
        bytes: The path of the new directory.
    """
    dir = "new dir"
    root = tkinter.Tk()
    root.title("New Dir")
    canvas1 = tkinter.Canvas(root, width=400, height=300)
    canvas1.pack()
    entry1 = tkinter.Entry(root)
    entry1.insert(tkinter.END, "new dir")
    entry1.pack()
    canvas1.create_window(200, 140, window=entry1)

    def new_name():
        nonlocal dir
        dir = entry1.get()
        root.destroy()

    button1 = tkinter.Button(text="create", command=new_name)
    canvas1.create_window(200, 180, window=button1)
    root.mainloop()
    dir = dir.replace("\\", "")
    dir = dir.replace(" ", "_")
    dir = dir.replace("~", "")
    dir = dir.replace("|", "")

    return os.path.join(path, dir.encode())


def share():
    """
    Function to manage access rights to a file or directory.

    Returns:
        tuple: The name and permission level (viewer/editor) of the user.
    """
    name = ""
    root = tkinter.Tk()
    root.title("Share")
    canvas1 = tkinter.Canvas(root, width=400, height=300)
    canvas1.pack()
    entry1 = tkinter.Entry(root)
    entry1.insert(tkinter.END, name)
    entry1.pack()
    canvas1.create_window(200, 140, window=entry1)

    def new_name():
        nonlocal name
        name = entry1.get()
        root.destroy()

    button1 = tkinter.Button(text="Share", command=new_name)
    canvas1.create_window(200, 180, window=button1)

    perm = tkinter.StringVar()
    perm.set("viewer")
    R1 = tkinter.Radiobutton(root, text="viewer", variable=perm, value="viewer")
    R1.pack(anchor=tkinter.W)
    canvas1.create_window(200, 60, window=R1)
    R1.select()
    R2 = tkinter.Radiobutton(root, text="editor", variable=perm, value="editor")
    R2.pack(anchor=tkinter.W)
    canvas1.create_window(200, 80, window=R2)
    R2.deselect()

    root.mainloop()

    return name.encode(), str(perm.get()).encode()
