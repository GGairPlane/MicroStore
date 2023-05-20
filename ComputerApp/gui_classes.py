import pygame as pg


class Button(pg.sprite.Sprite):
    # a class for creating a button in pg with hovers abd clicks. rounded corners rectangles.
    def __init__(self, color, x, y, width, height, id, text='', text_color=(0, 0, 0), hover_color=(100, 100, 100), hover_text=(200, 200, 200)):
        pg.sprite.Sprite.__init__(self)
        self.def_color = color
        self.def_text = text_color
        self.color = color
        self.text_color = text_color
        self.hover_color = hover_color
        self.hover_text = hover_text
        self.text = text
        self.rect = pg.Rect(x, y, width, height,)
        self.active = False
        self.hover = False
        self.clicked = False
        #self.id = id

    def draw(self, win, outline=0, font_size = 40):
        # draws the button on the screen
        pg.draw.rect(win, self.color, self.rect, outline)
        
        if self.text != '' :
            font = pg.font.SysFont('Brush Script MT', font_size)
            if font.size(self.text)[0] < 150:
                text = font.render(self.text, 1, self.text_color)             
            else: 
                text = font.render(self.text[:int(self.rect.width/(font_size/3))]+'...', 1, self.text_color)  
            win.blit(text, (self.rect.x + (self.rect.width / 2 - text.get_width() / 2),
                        self.rect.y + (self.rect.height / 2 - text.get_height() / 2)))
                

    def isOver(self, pos):
        # returns true if the mouse is over the button
        if self.rect.collidepoint(pos):
            self.active = True
            self.hover = True
            self.color = self.hover_color
            self.text_color = self.hover_text
        else:
            self.active = False
            self.hover = False
            self.color = self.def_color
            self.text_color = self.def_text

    def click(self, pos):
        # returns true if the mouse is clicked on the button
        if self.rect.collidepoint(pos):
            self.clicked = True
        else:
            self.clicked = False



    def draw_text(self, win, text, font, color):
        # draws text on the button
        if font.size(self.text)[0] < 200:
            textSurface = font.render(text, True, color)
            textRect = textSurface.get_rect()
            textRect.center = (self.rect.x + (self.rect.width / 2),
                            self.rect.y + (self.rect.height / 2))
            
    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y


COLOR_INACTIVE = (150,174,218)
COLOR_ACTIVE = (0, 0, 0)


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        FONT = pg.font.SysFont('Brush Script MT', 40)
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        FONT = pg.font.SysFont('Brush Script MT', 40)
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
                self.text = ""
                self.txt_surface = FONT.render(self.text, True, self.color)
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    self.active = False
                    self.color = COLOR_INACTIVE
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]

                else:
                    self.text += event.unicode
                # Re-render the text.
                if FONT.size(self.text)[0] < 240:
                    self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):

        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)
        
class PassBox(InputBox):
    def handle_event(self, event):
        super().handle_event(event)
        FONT = pg.font.SysFont('Brush Script MT', 40)
        if FONT.size(self.text)[0] < 240 and self.active:
                    self.txt_surface = FONT.render("*"*len(self.text), True, self.color)
        
    


class File_But(Button):
    def __init__(self, fname, path, id, x, y):
        super().__init__((209,225,255), x, y, 150, 75, id, fname, text_color=(40, 40, 40), hover_color=(150,174,218), hover_text=(40, 40, 40))
        self.fname = fname
        self.path = path

    def draw(self, win):
        return super().draw(win, 0, 20)
    

class Dir_But(Button):
    def __init__(self, dname, path, id, x, y):
        super().__init__((209,225,255), x, y, 150, 75, id, dname, text_color=(40, 40, 40), hover_color=(150,174,218), hover_text=(40, 40, 40))
        self.dname = dname
        self.path = path
        
    def draw(self, win):
        return super().draw(win, 0, 20)
    

            

class Shared_File_But(File_But):
    def __init__(self, fname, perm, uuid, path, id, x, y):
        super().__init__(fname, path, id, x, y)
        self.perm = perm
        self.uuid = uuid

    def draw(self, win):
        super().draw(win)
        
        font = pg.font.SysFont('Brush Script MT', 20)
        text = font.render(self.perm, 1, self.text_color)      

        win.blit(text, (self.rect.x + 3, self.rect.y + 3))
        
    
