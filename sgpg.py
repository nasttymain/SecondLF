#_20231009

import pygame
import pygame.locals
import time

class sgpg:
    def __init__(self) -> None:
        pygame.init()
        self.xpos = 0
        self.ypos = 0
        self.fontsize = 16
        self.fontobject = pygame.font.SysFont(None, self.fontsize)
        self.colorv = [0, 0, 0, 255]
        self.xalign = 0
        self.eventclbk = dict()
        self.pginfo = {
            "sx": 0,
            "sy": 0,
            "dispx": pygame.display.Info().current_w,
            "dispy": pygame.display.Info().current_h
        }
        self.surface = None
        self.fontfamily = None
        self.drawlasttime = time.time_ns() // 1000000 

        self.logmesonscreen = 0
        self.logmes_ypos = 0
        self.pushedkeylist = dict()
    def screen(self, screen_id: int, xsize: int, ysize: int, window_mode: int = 0) -> int:
        if screen_id != 0:
            return 1
        option = 0
        if (window_mode & 32) == 32:
            option += pygame.DOUBLEBUF + pygame.RESIZABLE
        if (window_mode & 64) == 64:
            option += pygame.FULLSCREEN
        self.surface = pygame.display.set_mode((xsize,ysize), option)
        self.surface.fill([255,255,255])
        self.pginfo["sx"] = self.surface.get_width()
        self.pginfo["sy"] = self.surface.get_height()
        self.xshift = 0
        self.yshift = 0
        return 0
    
    def ginfo(self, key: str) -> int|str|None:
        if key in self.pginfo:
            self.pginfo["cx"] = self.xpos
            self.pginfo["cy"] = self.ypos
            return self.pginfo[key]
        else:
            return None

    def logmes(self, text: str, errorlevel: int = 0) -> None:
        for tline in str(text).splitlines():
            print(tline)
            if self.surface != None and self.logmesonscreen != 0:
                if errorlevel == 2:
                    c = [255, 0, 0]
                elif errorlevel == 1:
                    c = [224, 152, 0]
                else:
                    c = [64, 64, 64]
                t = pygame.font.SysFont("monospace", 13).render(tline, False, c)
                pygame.draw.rect(self.surface, [255, 255, 255], (0, self.logmes_ypos, t.get_width(), t.get_height()), 0)
                self.surface.blit(t, (0, self.logmes_ypos))
                self.logmes_ypos = (self.logmes_ypos + t.get_height()) % self.surface.get_height()
                self.redraw_now()

    def cls(self, cls_mode: int = 0) -> None:
        self.clear()
        self.logmes_ypos = 0

    def pos_shift(self, xshift: int|float = 0, yshift: int|float = 0) -> None:
        self.xpos += int(xshift)
        self.ypos += int(yshift)

    def pos_shiftf(self, xshift: int|float = 0, yshift: int|float = 0) -> None:
        self.xpos += int(self.surface.get_width() * xshift) 
        self.ypos += int(self.surface.get_height() * yshift) 

    def pos(self, xposition: int|float, yposition: int|float) -> None:
        self.xpos = int(xposition)
        self.ypos = int(yposition)
    
    def posf(self, xposition: float, yposition: float) -> None:
        self.xpos = int(self.surface.get_width() * xposition) 
        self.ypos = int(self.surface.get_height() * yposition) 

    def font(self, font_name: str, font_size: str = 16) -> None:
        self.fontfamily = font_name
        self.fontsize = font_size
        if font_name == "":
            self.fontobject = pygame.font.SysFont(None, self.fontsize)
        else:
            self.fontobject = pygame.font.Font(self.fontfamily, self.fontsize)

    def text(self, message: object, noreturn_flag: int = 0) -> None:
        for tline in str(message).splitlines():
#            if self.fontfamily == None:
#            else:
#                t = pygame.font.Font(self.fontfamily, self.fontsize).render(tline, True, self.colorv)
            t = self.fontobject.render(tline, True, self.colorv)
            #pygame.draw.rect(self.surface, [255,192,192], (self.xpos, self.ypos, t.get_width(), t.get_height()), 0)
            if self.xalign == 0:
                #LEFT
                self.surface.blit(t, (self.xpos, self.ypos))
            elif self.xalign == 1:
                #CENTER
                self.surface.blit(t, (self.xpos - t.get_width() / 2, self.ypos - t.get_height() / 2))
            if noreturn_flag == 0:
                self.ypos += t.get_height()

    def align(self, alignment_value: str = "left") -> None:
        for av in alignment_value.split():
            if av == "left":
                self.xalign = 0
            elif av == "center":
                self.xalign = 1

    def color(self, red: int, green: int, blue: int, alpha: int = 255) -> None:
        self.colorv = [red, green, blue, alpha]
    def rgbcolor(self, rgb: int, alpha: int = 255) -> None:
        self.colorv = [rgb // 65536, rgb % 65536 // 256, rgb % 256, alpha]

    def line(self, x1: int|float, y1: int|float, x2: int|float, y2: int|float, line_width: int = 1) -> None:
        pygame.draw.line(self.surface, self.colorv, (x1, y1), (x2, y2), line_width)

    def box(self, x1: int|float, y1: int|float, x2: int|float, y2: int|float, boxline_width: int = 1) -> None:
        pygame.draw.rect(self.surface, self.colorv, (x1, y1, x2 - x1, y2 - y1), boxline_width)

    def clear(self) -> None:
        pygame.draw.rect(self.surface, (255, 255, 255), (0, 0, self.surface.get_width(), self.surface.get_height()))

    def fill(self, x1: int|float = None, y1: int|float = None, x2: int|float = None, y2: int|float = None) -> None:
        if x1 == y1 == x2 == y2 == None:
            #boxf:
            self.box(0, 0, self.surface.get_width(), self.surface.get_height(), 0)
        else:
            self.box(x1, y1, x2, y2, 0)

    def neweventhandler(self, event_name: str, function_pointer: callable) -> None:
        self.eventclbk[event_name] = function_pointer

    def stop(self) -> None:
        game_close = 0
        pygame.display.flip()
        while game_close == 0:
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.locals.QUIT:
                    game_close = 1
                elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        #LEFT
                        if self.eventclbk.get("PG_MBUTTONDOWN") != None:
                            self.eventclbk["PG_MBUTTONDOWN"](event.pos[0], event.pos[1])
                elif event.type == pygame.locals.KEYDOWN:
                    if event.dict["scancode"] in self.pushedkeylist.keys():
                        self.pushedkeylist[event.dict["scancode"]]["holdtime"] = time.time_ns() // 1000000
                        self.pushedkeylist[event.dict["scancode"]]["holdcounter"] = 6
                    else:
                        self.pushedkeylist[event.dict["scancode"]] = dict()
                        self.pushedkeylist[event.dict["scancode"]]["unicode"] = event.dict["unicode"]
                        self.pushedkeylist[event.dict["scancode"]]["holdtime"] = time.time_ns() // 1000000
                        self.pushedkeylist[event.dict["scancode"]]["holdcounter"] = 6
                    if self.eventclbk.get("PG_KEYDOWN") != None:
                        self.eventclbk["PG_KEYDOWN"](self.pushedkeylist[event.dict["scancode"]]["unicode"], event.dict["scancode"])
                elif event.type == pygame.locals.KEYUP:
                    if event.dict["scancode"] in self.pushedkeylist.keys():
                        self.pushedkeylist.pop(event.dict["scancode"])
                    else:
                        pass
                elif event.type == pygame.locals.WINDOWRESIZED:
                    self.pginfo["sx"] = self.surface.get_width()
                    self.pginfo["sy"] = self.surface.get_height()
                    if self.eventclbk.get("PG_WINDOWRESIZED") != None:
                        self.eventclbk["PG_WINDOWRESIZED"](self.surface.get_width(), self.surface.get_height())
                elif event.type == pygame.locals.ACTIVEEVENT:
                    if (event.state, event.gain) == (2, 1):
                        self.pginfo["act"] = 0
                    elif (event.state, event.gain) == (2, 0):
                        self.pushedkeylist = dict()
                        self.pginfo["act"] = -1
            # 1 time for every frame loop
            for pkk in self.pushedkeylist.keys():
                if time.time_ns() // 1000000 - self.pushedkeylist[pkk]["holdtime"] >= 450:
                    if (time.time_ns() // 1000000 - self.pushedkeylist[pkk]["holdtime"]) // 75 > self.pushedkeylist[pkk]["holdcounter"]:
                        self.pushedkeylist[pkk]["holdcounter"] = (time.time_ns() // 1000000 - self.pushedkeylist[pkk]["holdtime"]) // 75
                        if "PG_KEYDOWN" in self.eventclbk:
                            self.eventclbk["PG_KEYDOWN"](self.pushedkeylist[pkk]["unicode"], pkk)
            if self.eventclbk.get("PG_TICK") != None:
                self.eventclbk["PG_TICK"]()
            pygame.display.flip()

    def title(self, title_text: str = "") -> None:
        pygame.display.set_caption(title_text)
        pass
    def redraw_now(self) -> None:
        pygame.display.flip()

    def mouse(self, x: int|float|None = None, y: int|float|None = None) -> None:
        if x == None and y == None:
            pygame.mouse.set_visible(True)
        elif x < 0 or y < 0:
            pygame.mouse.set_visible(False)

    def end(self):
        pygame.quit()

