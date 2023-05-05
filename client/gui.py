import os
import threading
import time
from pdb import Restart

import glbl
import pygame as pg
from gui_classes import *
from tcp_by_size import *

from client import *

REFRESH_RATE = 60


def init():
    global win, clock, bg1, bg2
    pg.init()
    os.chdir(os.path.split(os.path.realpath(__file__))[0])
    clock = pg.time.Clock()
    win = pg.display.set_mode((1920, 1080))
    pg.display.set_caption('"DROPBOX"')
    bg1 = pg.image.load("assets/bg.png")
    bg2 = pg.image.load("assets/bg1.png")
    cloud_icon = pg.image.load("assets/cloud.png")
    pg.display.set_icon(cloud_icon)
    win.blit(bg1, (0, 0))


def reset():
    global to_send, sent, t_die, tid, threads, recieve, recieved
    glbl.to_send = b""
    glbl.sent = True
    glbl.t_die = []
    tid = 1
    threads = []
    glbl.recieved = False
    glbl.recieve = b""


def main():
    global win, tid, threads
    glbl.globals()
    init()

    username = InputBox(890, 500, 200, 32, "username")
    password = PassBox(890, 650, 200, 32, "password")
    ip_box = InputBox(245, 262, 250, 32, "127.0.0.1")
    input_boxes = [username, password, ip_box]

    login_button = Button((209, 225, 255), 850, 300, 100, 100, 0, "login", (0, 0, 0))
    signup_button = Button((209, 225, 255), 1050, 300, 100, 100, 0, "signup", (0, 0, 0))
    join_button = Button(
        (209, 225, 255), 950, 780, 100, 100, 0, "Join", (209, 225, 255)
    )

    run = True
    while run:
        try:
            reset()

            loggedin = False
            login_type = "l"
            selected = pg.Rect(
                845,
                295,
                110,
                110,
            )

            while not loggedin:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        glbl.t_die.append("all")
                        if "t" in locals():
                            t.join()
                        pg.quit()
                        raise StopIteration
                    elif event.type == pg.KEYDOWN:
                        for box in input_boxes:
                            box.handle_event(event)
                    elif event.type == pg.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            for box in input_boxes:
                                box.handle_event(event)
                            if login_button.rect.collidepoint(event.pos):
                                login_type = "l"
                                selected = pg.Rect(
                                    845,
                                    295,
                                    110,
                                    110,
                                )
                            elif signup_button.rect.collidepoint(event.pos):
                                login_type = "s"
                                selected = pg.Rect(
                                    1045,
                                    295,
                                    110,
                                    110,
                                )
                            elif join_button.rect.collidepoint(event.pos):
                                t = threading.Thread(
                                    target=main_client, args=((tid, ip_box.text))
                                )
                                t.start()
                                tid += 1
                                threads.append(t)
                                glbl.to_send = signin(
                                    login_type, username.text, password.text
                                )
                                glbl.sent = False
                                pg.time.wait(10)
                                start_time = time.time()
                                while not glbl.recieved:
                                    if time.time() - start_time > 5:
                                        print("timeout error")
                                        break
                                    pass
                                if (
                                    glbl.recieve == b"LOGAK~Login success"
                                    or glbl.recieve == b"LOGAK~Signup success"
                                ):
                                    loggedin = True
                                    glbl.recieved = False
                                    break
                                else:
                                    glbl.t_die.append(tid)
                                    if "t" in locals():
                                        t.join(0.1)
                                        raise Restart

                win.blit(bg1, (0, 0))

                for box in input_boxes:
                    box.draw(win)

                login_button.draw(win)
                signup_button.draw(win)
                join_button.draw(win, 2)
                pg.draw.rect(win, (209, 225, 255), selected, 2)
                pg.display.update()
                clock.tick(REFRESH_RATE)

            time_delay = 1000
            timer_event = pg.USEREVENT + 1

            download_button = Button(
                (54, 76, 111), 0, 0, 150, 75, 0, "Download", (209, 225, 255)
            )
            cd_button = Button(
                (54, 76, 111), 0, 0, 150, 75, 0, "Enter", (209, 225, 255)
            )
            reomve_button = Button(
                (54, 76, 111), 150, 0, 150, 75, 0, "Remove", (209, 225, 255)
            )
            copy_button = Button(
                (54, 76, 111), 300, 0, 150, 75, 0, "Copy", (209, 225, 255)
            )
            cut_button = Button(
                (54, 76, 111), 450, 0, 150, 75, 0, "Cut", (209, 225, 255)
            )
            rename_button = Button(
                (54, 76, 111), 600, 0, 150, 75, 0, "Rename", (209, 225, 255)
            )
            share_button = Button(
                (54, 76, 111), 750, 0, 150, 75, 0, "Share", (209, 225, 255)
            )
            logout_button = Button(
                (209, 225, 255), 1750, 20, 120, 50, 0, "Logout", (209, 225, 255)
            )
            home_button = Button(
                (209, 225, 255), 1600, 20, 120, 50, 0, "Home", (209, 225, 255)
            )
            back_button = Button(
                (209, 225, 255), 1300, 20, 120, 50, 0, "Back", (209, 225, 255)
            )
            shared_button = Button(
                (209, 225, 255), 1450, 20, 120, 50, 0, "Shared", (209, 225, 255)
            )

            paste_button = Button(
                (54, 76, 111), 0, 0, 150, 75, 0, "Paste", (209, 225, 255)
            )
            upload_button = Button(
                (54, 76, 111), 0, 0, 150, 75, 0, "Upload", (209, 225, 255)
            )
            mkdir_button = Button(
                (54, 76, 111), 0, 0, 150, 75, 0, "New Dir", (209, 225, 255)
            )

            dir_update = False
            req_dir = ""
            curr_dir = ""
            curr_file = ""
            file_selected = False
            dir_selected = False
            right_selected = False
            copy = ""
            cut = ""
            while True:
                if not dir_update:
                    dir_update = True
                    files = pg.sprite.Group()
                    files.empty()
                    if curr_dir == "|":
                        glbl.to_send = protocol_build_request("getshare")
                    else:
                        glbl.to_send = protocol_build_request(
                            "cd", os.path.join(curr_dir, req_dir)
                        )
                    glbl.sent = False
                    while not glbl.recieved:
                        pass
                    print(glbl.recieve)

                    if type(glbl.recieve) != list:
                        continue

                    id = 1
                    x = 100
                    y = 100
                    if req_dir == ".":
                        curr_dir = curr_dir
                    elif req_dir == "..":
                        curr_dir = os.path.split(curr_dir)[0]
                    else:
                        curr_dir = os.path.join(curr_dir, req_dir)
                    req_dir = ""

                    if curr_dir == "|":
                        for file in glbl.recieve[1]:
                            files.add(
                                Shared_File_But(
                                    file[0], file[1], file[2], curr_dir, id, x, y
                                )
                            )
                            id += 1
                            x += 200
                            if x >= 1800:
                                x = 100
                                y += 200
                    else:
                        for dir in glbl.recieve[0]:
                            files.add(Dir_But(dir, curr_dir, id, x, y))
                            id += 1
                            x += 200
                            if x >= 1800:
                                x = 100
                                y += 200
                        for file in glbl.recieve[1]:
                            files.add(File_But(file, curr_dir, id, x, y))
                            id += 1
                            x += 200
                            if x >= 1800:
                                x = 100
                                y += 200

                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        glbl.t_die.append("all")
                        t.join(0.1)
                        pg.quit()
                        raise StopIteration

                    elif event.type == timer_event:
                        dir_update = False

                    elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                        if len(curr_dir) != 0 and curr_dir[0] == "|":
                            right_selected = False
                            pg.time.set_timer(timer_event, time_delay, 1)

                            if logout_button.rect.collidepoint(event.pos):
                                glbl.to_send = protocol_build_request("exit")
                                glbl.sent = False
                                glbl.t_die.append(tid)
                                if "t" in locals():
                                    t.join(0.1)
                                raise Restart

                            elif home_button.rect.collidepoint(event.pos):
                                curr_dir = ""
                                req_dir = ""
                                curr_file = ""
                                files.empty()
                                file_selected = False
                                dir_selected = False
                            elif shared_button.rect.collidepoint(event.pos):
                                curr_dir = "|"
                                req_dir = ""
                                curr_file = ""
                                files.empty()
                                file_selected = False
                                dir_selected = False


                            elif file_selected:
                                file_selected = False
                                if reomve_button.rect.collidepoint(event.pos):
                                    glbl.to_send = protocol_build_request(
                                        "remove", "|" + curr_file.uuid
                                    )
                                    glbl.sent = False

                                elif copy_button.rect.collidepoint(event.pos):
                                    copy = os.path.join(curr_dir, "|", curr_file.uuid)
                                    cut = ""
                                elif cut_button.rect.collidepoint(event.pos):
                                    cut = os.path.join(curr_dir, "|", curr_file.uuid)
                                    copy = ""
                                elif rename_button.rect.collidepoint(event.pos):
                                    glbl.to_send = protocol_build_request(
                                        "rename", "|" + curr_file.uuid
                                    )
                                    glbl.sent = False
                                elif share_button.rect.collidepoint(event.pos):
                                    glbl.to_send = protocol_build_request(
                                        "share", "|" + curr_file.uuid
                                    )
                                    glbl.sent = False

                                elif download_button.rect.collidepoint(event.pos):
                                    glbl.to_send = protocol_build_request(
                                        "download", "|" + curr_file.uuid
                                    )
                                    glbl.sent = False
                            elif dir_selected:
                                dir_selected = False
                                if reomve_button.rect.collidepoint(event.pos):
                                    glbl.to_send = protocol_build_request(
                                        "remove", "|" + curr_file.uuid
                                    )
                                    glbl.sent = False

                                elif cd_button.rect.collidepoint(event.pos):
                                    req_dir = "|" + curr_file.uuid
                                    curr_file = ""
                                    files.empty()

                                elif copy_button.rect.collidepoint(event.pos):
                                    copy = "|" + curr_file.uuid
                                    cut = ""
                                elif cut_button.rect.collidepoint(event.pos):
                                    cut = "|" + curr_file.uuid
                                    copy = ""
                                elif rename_button.rect.collidepoint(event.pos):
                                    dir_update = True
                                    glbl.to_send = protocol_build_request(
                                        "rename", "|" + curr_file.uuid
                                    )
                                    glbl.sent = False
                                elif share_button.rect.collidepoint(event.pos):
                                    glbl.to_send = protocol_build_request(
                                        "share", "|" + curr_file.uuid
                                    )
                                    glbl.sent = False

                            elif paste_button.rect.collidepoint(event.pos):
                                if copy != "":
                                    glbl.to_send = protocol_build_request(
                                        "copy", copy, os.path.join(curr_dir, copy)
                                    )
                                    glbl.sent = False

                                elif cut != "":
                                    glbl.to_send = protocol_build_request(
                                        "cut", cut, os.path.join(curr_dir, copy)
                                    )
                                    glbl.sent = False

                            elif upload_button.rect.collidepoint(event.pos):
                                dir_update = True
                                with threading.Lock():
                                    glbl.to_send = protocol_build_request("upload")

                                time.sleep(0.1)
                                glbl.sent = False

                            elif mkdir_button.rect.collidepoint(event.pos):
                                glbl.to_send = protocol_build_request("new dir")
                                glbl.sent = False

                            for file in files:
                                if file.rect.collidepoint(event.pos):
                                    if type(file) == Dir_But:
                                        curr_file = file
                                        dir_selected = True
                                        file_selected = False
                                    else:
                                        curr_file = file
                                        file_selected = True
                                        dir_selected = False
                                    break
                        else:
                            right_selected = False
                            pg.time.set_timer(timer_event, time_delay, 1)

                            if logout_button.rect.collidepoint(event.pos):
                                glbl.to_send = protocol_build_request("exit")
                                glbl.sent = False
                                glbl.t_die.append(tid)
                                if "t" in locals():
                                    t.join(0.1)
                                raise Restart

                            elif home_button.rect.collidepoint(event.pos):
                                curr_dir = ""
                                req_dir = ""
                                curr_file = ""
                                files.empty()
                                file_selected = False
                                dir_selected = False
                            elif shared_button.rect.collidepoint(event.pos):
                                curr_dir = "|"
                                req_dir = ""
                                curr_file = ""
                                files.empty()
                                file_selected = False
                                dir_selected = False
                            elif back_button.rect.collidepoint(event.pos):
                                curr_dir = os.path.split(curr_dir)[0]
                                print(curr_dir)
                                req_dir = ""
                                curr_file = ""
                                files.empty()
                                file_selected = False
                                dir_selected = False                            

                            elif file_selected:
                                file_selected = False
                                if reomve_button.rect.collidepoint(event.pos):
                                    glbl.to_send = protocol_build_request(
                                        "remove", curr_file.text
                                    )
                                    glbl.sent = False

                                elif copy_button.rect.collidepoint(event.pos):
                                    copy = os.path.join(curr_dir, curr_file.text)
                                    cut = ""
                                elif cut_button.rect.collidepoint(event.pos):
                                    cut = os.path.join(curr_dir, curr_file.text)
                                    copy = ""
                                elif rename_button.rect.collidepoint(event.pos):
                                    glbl.to_send = protocol_build_request(
                                        "rename", os.path.join(curr_dir, curr_file.text)
                                    )
                                    glbl.sent = False
                                elif share_button.rect.collidepoint(event.pos):
                                    glbl.to_send = protocol_build_request(
                                        "share", os.path.join(curr_dir, curr_file.text)
                                    )
                                    glbl.sent = False

                                elif download_button.rect.collidepoint(event.pos):
                                    glbl.to_send = protocol_build_request(
                                        "download",
                                        os.path.join(curr_dir, curr_file.text),
                                    )
                                    glbl.sent = False
                            elif dir_selected:
                                dir_selected = False
                                if reomve_button.rect.collidepoint(event.pos):
                                    glbl.to_send = protocol_build_request(
                                        "remove", curr_file.text
                                    )
                                    glbl.sent = False

                                elif cd_button.rect.collidepoint(event.pos):
                                    req_dir = curr_file.text
                                    curr_file = ""
                                    files.empty()

                                elif copy_button.rect.collidepoint(event.pos):
                                    copy = os.path.join(curr_dir, curr_file.text)
                                    cut = ""
                                elif cut_button.rect.collidepoint(event.pos):
                                    cut = os.path.join(curr_dir, curr_file.text)
                                    copy = ""
                                elif rename_button.rect.collidepoint(event.pos):
                                    dir_update = True
                                    glbl.to_send = protocol_build_request(
                                        "rename", os.path.join(curr_dir, curr_file.text)
                                    )
                                    glbl.sent = False
                                elif share_button.rect.collidepoint(event.pos):
                                    glbl.to_send = protocol_build_request(
                                        "share", os.path.join(curr_dir, curr_file.text)
                                    )
                                    glbl.sent = False

                            elif paste_button.rect.collidepoint(event.pos):
                                if copy != "":
                                    glbl.to_send = protocol_build_request(
                                        "copy", copy, os.path.join(curr_dir, copy)
                                    )
                                    glbl.sent = False

                                elif cut != "":
                                    glbl.to_send = protocol_build_request(
                                        "cut", cut, os.path.join(curr_dir, copy)
                                    )
                                    glbl.sent = False

                            elif upload_button.rect.collidepoint(event.pos):
                                dir_update = True
                                with threading.Lock():
                                    glbl.to_send = protocol_build_request("upload")

                                time.sleep(0.1)
                                glbl.sent = False

                            elif mkdir_button.rect.collidepoint(event.pos):
                                glbl.to_send = protocol_build_request("new dir")
                                glbl.sent = False

                            for file in files:
                                if file.rect.collidepoint(event.pos):
                                    if type(file) == Dir_But:
                                        curr_file = file
                                        dir_selected = True
                                        file_selected = False
                                    else:
                                        curr_file = file
                                        file_selected = True
                                        dir_selected = False
                                    break

                    elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                        paste_button.rect.x = event.pos[0]
                        paste_button.rect.y = event.pos[1]
                        upload_button.rect.x = event.pos[0]
                        upload_button.rect.y = event.pos[1] + 75
                        mkdir_button.rect.x = event.pos[0]
                        mkdir_button.rect.y = event.pos[1] + 150
                        right_selected = not right_selected

                if glbl.recieved == True:
                    glbl.recieve = b""
                    glbl.recieved = False

                win.blit(bg2, (0, 0))
                for file in files:
                    file.isOver(pg.mouse.get_pos())
                    file.draw(win)
                if file_selected:
                    reomve_button.draw(win)
                    download_button.draw(win)
                    copy_button.draw(win)
                    cut_button.draw(win)
                    rename_button.draw(win)
                    share_button.draw(win)
                elif dir_selected:
                    cd_button.draw(win)
                    reomve_button.draw(win)
                    copy_button.draw(win)
                    cut_button.draw(win)
                    rename_button.draw(win)
                    share_button.draw(win)
                elif right_selected:
                    paste_button.draw(win)
                    upload_button.draw(win)
                    mkdir_button.draw(win)

                logout_button.draw(win, 2)
                home_button.draw(win, 2)
                shared_button.draw(win, 2)
                back_button.draw(win, 2)
                pg.display.update()
                clock.tick(REFRESH_RATE)

        except StopIteration:
            break
        except Restart:
            continue


if __name__ == "__main__":
    main()
