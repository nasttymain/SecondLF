import sgpg
import os.path
import json
import traceback, sys
import importlib
import time
import decimal
import tkinter.filedialog
import tkinter.simpledialog


#関数間でデータ交換するためのゴッドオブジェクト(つまりゴミ)
class lfapp_struct():
    def __init__(self) -> None:
        self.controller_app_conf: dict = dict()
        self.controller_app_state: dict = dict()
        self.appconf: dict = dict()
        self.devconf: dict = dict()
        self.beatdev_obj: object = None
        self.physidev_conf: dict = dict()
        self.logidev_conf: dict = dict()
        self.physidev_conf: dict = dict()
        self.physidev_mod: object = None
        self.physidev_obj: object = None
        self.logidev_obj: object = None
        self.primdev_obj: object = None
        self.primdev_conf: object = None
        self.keyconf: dict = dict()
        self.profile_conf: dict = dict()
        self.profile_state: dict = {"avail": 0, "filename": "", "page": 0, "screenname": ""}

# 設定ファイルのロードと各モジュールの初期化
def app_init() -> None:
    g.logmesonscreen = 1
    g.color(64, 64, 64)
    g.fill()
    g.logmes("[slf] Hello, World!")
    try:

        a.beatdev_obj = importlib.import_module("vulcbeat").beatmanager()
        g.logmes("[slf]Initialized vulcbeat beat manager")

        a.appconf = dict()
        with open("config.json", "r") as f:
            pass
            a.appconf = json.load(f)
            g.logmes("[slf]Loaded config.json")
        a.keyconf = {
            "charcodelist": [],
            "scancodelist": [],
            "commandlist": [],
        }

        for kbcnt, kb in enumerate(a.appconf["keybdbinds"]):
            if "charcode" in kb.keys():
                a.keyconf["charcodelist"].append(kb["charcode"])
            else:
                a.keyconf["charcodelist"].append(None)
            if "scancode" in kb.keys():
                a.keyconf["scancodelist"].append(kb["scancode"])
            else:
                a.keyconf["scancodelist"].append(None)
            if "command" in kb.keys():
                a.keyconf["commandlist"].append(kb["command"])
            else:
                a.keyconf["commandlist"].append("")
        
        if "terminal" in a.appconf["controller"].keys():
            if a.appconf["controller"]["terminal"] in ["fullcolor", "palcolor"]:
                print("[SecondLF] List of keyboard-bound colors are:")
                for kbcnt, kb in enumerate(a.appconf["keybdbinds"]):
                    if "command" in kb.keys():
                        if "charcode" in kb.keys() and kb["command"].split(" ")[0].upper() == "COLOR.TOGGLE":
                            cl = kb["command"].split(" ")[1]
                            if cl.startswith("#"):
                                try:
                                    cl = int("0x" + cl[1:], 16)
                                except ValueError as e:
                                    cl = 0
                            else:
                                try:
                                    cl = int(cl)
                                except ValueError as e:
                                    cl = 0
                            print("\x1b[48;2;" + str(cl // 65536) + ";" + str(cl % 65536 // 256) + ";" + str(cl % 256) + "m", end="")
                            print(" " + kb["charcode"] + " ", end="")
                            print("\x1b[0m ", end="")
                print("\x1b[0m")
            
        a.devconf = a.appconf["deviceconf"]
        a.physidev_conf = a.devconf["physicallight"]
        a.logidev_conf = a.devconf["logicaldevices"]
        a.physidev_mod = importlib.import_module("drivers." + a.physidev_conf["driver"])
        a.physidev_obj = a.physidev_mod.physical_driver(a.physidev_conf["option"], g.logmes)
        g.logmes("[slf]Initialized physical driver named \"" + a.physidev_conf["driver"] + "\"")
        
        a.logidev_obj = []
        for lecnt, le in enumerate(a.logidev_conf):
            if "name" not in le:
                g.logmes("[slf]  WARN: The " + str(lecnt) + "(st/nd/rd/th) entry is invalid and skipped loading", errorlevel = 1)
                continue
            if le["driver"] != None and le["driver"] != "":
                if os.path.isfile("drivers/" + le["driver"] + ".py"):
                    a.logidev_obj.append(
                        importlib.import_module("drivers." + le["driver"]).light_driver(le["mode"], le["option"])
                    )
                    for c in a.logidev_obj[-1].reset().items():
                        a.physidev_obj.set(c[0], c[1]["value"])
                    g.logmes("[slf]    OK: Loaded \"" + le["driver"] + "\" for \"" + le["name"] + "\"")
                else:
                    a.logidev_obj.append(None)
                    g.logmes("[slf]  WARN: Could not find the driver file \"" + le["name"] + "\"", errorlevel = 1)
            else:
                a.logidev_obj.append(None)
                g.logmes("[slf]  WARN: The driver description of \"" + le["name"] + "\" is invalid and skipped loading", errorlevel = 1)
        g.logmes("[slf] Initialized all logical drivers")

        for ck in a.appconf["controller"].keys():
            a.controller_app_conf[ck] = a.appconf["controller"][ck]

        a.primdev_conf = a.controller_app_conf["primary-controller"]
        a.primdev_obj = importlib.import_module("drivers." + a.controller_app_conf["primary-controller"]["driver"]).primary_driver(a.beatdev_obj)
        a.primdev_obj.actionclbkset(primarysetter)
        a.primdev_obj.bankset(a.controller_app_state["primary-bank"])
        a.primdev_obj.faderset(a.controller_app_state["primary-fader"])
        g.logmes("[slf] Initialized primary driver.")

        a.controller_app_conf["keybd-handler"] = importlib.import_module("drivers." + a.controller_app_conf["keybd-modname"]).keybdsettings()
        g.logmes("[slf] Initialized keyboard handler named \"" + a.controller_app_conf["keybd-modname"] + "\"")

        g.neweventhandler("PG_WINDOWRESIZED", app_proc_windowresized)
        g.neweventhandler("PG_TICK", app_proc_tick)
        g.neweventhandler("PG_KEYDOWN", app_proc_keydown)
        g.neweventhandler("PG_MBUTTONDOWN", app_proc_mbuttondown)

        g.logmes("[slf] Initialization finished :)")


        app_draw_screen()
        g.logmesonscreen = 0

    except Exception as e:
        for t in traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]) :
            g.logmes(t, errorlevel = 2)
        globals()["errorflag"] += 1

# 画面の再描画
def app_draw_screen() -> None:
    fontsize = a.controller_app_conf["font-size"]
    g.cls(0)
    g.rgbcolor(a.controller_app_conf["ui-background-color"])
    g.fill()


    g.pos_shift()
    g.font("ipaexg.ttf", fontsize)


    # HEADER
    g.rgbcolor(a.controller_app_conf["ui-text-color"])
    g.align("center")
    g.pos(g.ginfo("sx") // 2, 24)
    g.text("(プロファイルなし)" if a.profile_state["avail"] == 0 else a.profile_state["screenname"], 1)
    g.pos_shiftf(-0.4, 0.0)
    g.text(str(a.controller_app_state["app-tps"]) + " TPS", 1)
    g.pos_shiftf(0.8, 0.0)
    if a.physidev_obj.isremotecontroller() == True:
        g.text("←-→  " + str(a.physidev_conf["option"]["port"]), 1)
    else:
        g.text("←X→  " + str(a.physidev_conf["option"]["port"]), 1)
        

    # COLOR
    g.rgbcolor(a.controller_app_conf["ui-text-color"])
    g.align("left")
    g.posf(0.1, 0.1)
    g.text("COLOR", 1)
    if a.controller_app_conf["light-color"] != dict():
        g.pos_shiftf(0.08, 0.0)
    else:
        g.pos_shift(fontsize * 4, 0.0)
        if a.controller_app_state["blackout"] == 1:
            g.line(g.ginfo("cx"), g.ginfo("cy") + fontsize // 2, 0.1 * g.ginfo("sx") - fontsize // 2, 0.1 * g.ginfo("sy") + fontsize // 2, 3)

    for ck, cv in a.controller_app_conf["light-color"].items():
        g.pos_shiftf(0.02, 0.0)
        g.rgbcolor(cv)
        g.fill(g.ginfo("cx"), g.ginfo("cy"), g.ginfo("cx") + fontsize, g.ginfo("cy") + fontsize)
        
        g.rgbcolor(0)
        g.pos_shift( 1,  1)
        g.text(ck, 1)

        g.rgbcolor(16777215)
        g.pos_shift(-1, -1)
        g.text(ck, 1)
        g.pos_shift(fontsize // 4, 0)
    if a.controller_app_state["blackout"] == 1 and a.controller_app_conf["light-color"] != dict():
        g.rgbcolor(a.controller_app_conf["ui-text-color"])
        g.line(0.10 * g.ginfo("sx") - fontsize // 2, 0.1 * g.ginfo("sy") + fontsize // 2, g.ginfo("cx") + fontsize * 1.5, 0.1 * g.ginfo("sy") + fontsize // 2, 3)

    g.posf(0.175, 0.1)
    g.pos_shiftf(0.0, 0.05)
    g.rgbcolor(a.controller_app_conf["ui-text-color"])
    g.text("BLACK OUT", 1)
    g.pos_shiftf(0.15, 0.0)
    g.text("Yes" if a.controller_app_state["blackout"] == 1 else "No")

    g.posf(0.175, 0.1)
    g.pos_shiftf(0.0, 0.1)
    g.text("BRIGHTNESS", 1)
    g.pos_shiftf(0.15, 0.0)
    g.text(a.controller_app_state["brightness"], 1)
    g.pos_shiftf(0.05, 0.0)
    if a.controller_app_state["brightness"] < a.controller_app_state["brightness-fader-target"]:
        g.text("↑")
    elif a.controller_app_state["brightness"] > a.controller_app_state["brightness-fader-target"]:
        g.text("↓")

    # DEVICE-INFO
    g.rgbcolor(a.controller_app_conf["ui-text-color"])
    g.align("left")
    g.posf(0.1, 0.3)
    g.text("DEVICES")

    for devcnt, dev in enumerate(a.logidev_obj):
        g.posf(0.125, 0.3)
        g.pos_shiftf(0.2 * (devcnt % 2), 0.05 * (1 + devcnt // 2))
        if "name" not in a.logidev_conf[devcnt]:
            continue
        g.rgbcolor(a.controller_app_conf["ui-text-color"])
        g.text(a.logidev_conf[devcnt]["name"], 1)
        g.pos_shiftf(0.1, 0.0)
        if dev == None:
            g.text("[ERROR]")
            continue
        if "displayparam" not in dir(dev):
            g.text("[NODISP]")
            continue
        for c in dev.displayparam():
            if c["category"] == "color.rgb" and c["type"] == "int":
                g.rgbcolor(c["value"])
                if "alloc" in c:
                    g.rgbcolor(
                        a.physidev_obj.get(c["alloc"] + 0) * 65536
                        +
                        a.physidev_obj.get(c["alloc"] + 1) * 256
                        +
                        a.physidev_obj.get(c["alloc"] + 2)
                               )
                g.fill(g.ginfo("cx"), g.ginfo("cy"), g.ginfo("cx") + fontsize, g.ginfo("cy") + fontsize)
                g.pos_shift(fontsize * 1.25, 0)


    # TIME
    g.rgbcolor(a.controller_app_conf["ui-text-color"])
    g.align("left")
    g.posf(0.525, 0.1)
    g.text("TIME", 1)
    g.pos_shiftf(0.075, 0.0)
    if (int(a.beatdev_obj.beatstamp[1] * 10)) <= 1:
        g.text("◯", 1)
    elif (int(a.beatdev_obj.beatstamp[1] * 10)) <= 3:
        g.text("o", 1)
    else:
        g.text(".", 1)
    g.pos_shiftf(0.025, 0.0)
    g.text("BR " + str(a.beatdev_obj.beatstamp[0] // a.beatdev_obj.beats + 1), 1)
    g.pos_shiftf(0.1, 0.0)
    g.text("BT " + str(a.beatdev_obj.beatstamp[0] % a.beatdev_obj.beats + 1), 1)
    g.pos_shiftf(0.1, 0.0)
    g.text("ST " + "{:#1d}".format(int(a.beatdev_obj.beatstamp[1] * 10)), 1)

    g.posf(0.6, 0.1)
    g.pos_shiftf(0.0, 0.05)
    g.text("BPM", 1)
    g.pos_shiftf(0.15, 0.0)
    g.text(str(a.beatdev_obj.bpm))

    g.posf(0.6, 0.1)
    g.pos_shiftf(0.0, 0.1)
    g.text("BEAT", 1)
    g.pos_shiftf(0.15, 0.0)
    g.text(str(a.beatdev_obj.beats))


    # PATTERN
    g.posf(0.525, 0.4)
    g.rgbcolor(a.controller_app_conf["ui-text-color"])
    g.align("left")
    g.text("PATTERN", 1)
    g.pos_shiftf(0.15, 0.0)
    g.text(a.controller_app_state["primary-bank"], 1)
    g.pos_shiftf(0.025, 0.0)
    g.text("(" + a.primdev_obj.bankinfo() + ")")

    g.posf(0.6, 0.4)
    g.pos_shiftf(0.0, 0.05)
    g.text("FADER", 1)
    g.pos_shiftf(0.15, 0.0)
    g.text(a.controller_app_state["primary-fader"])

    # PROFILE
    g.rgbcolor(a.controller_app_conf["ui-text-color"])
    g.align("left")
    g.posf(0.525, 0.6)
    g.text("PROFILE", 1)
    g.pos_shiftf(0.15, 0.0)
    g.text(os.path.basename(a.profile_state["filename"]) if a.profile_state["avail"] == 1 else "(No Profile)")
    g.box(g.ginfo("sx") * 0.85, g.ginfo("sy") * 0.6 - 2, g.ginfo("sx") * 0.95, g.ginfo("sy") * 0.6 + fontsize + 2)
    g.align("center")
    g.pos(g.ginfo("sx") * 0.9, g.ginfo("sy") * 0.6 + fontsize // 2)
    g.text("LOAD")
    if "pages" in a.profile_conf:
        g.align("left")
        g.posf(0.6, 0.6)
        g.pos_shiftf(0.0, 0.05)
        if str(a.profile_state["page"]) in a.profile_conf["pages"]:
            if "next_page" in a.profile_conf["pages"][str(a.profile_state["page"])]:
                nextpg = a.profile_conf["pages"][str(a.profile_state["page"])]["next_page"]
                if str(nextpg) in a.profile_conf["pages"].keys():
                    n = a.profile_conf["pages"][str(nextpg)]["explanation"] if "explanation" in a.profile_conf["pages"][str(nextpg)] else ""
                else:
                    n = "NOT FOUND (OR EOF)"
                g.text("NEXT [ " + ["J", "L"][a.profile_state["page"] % 2] + " ]", 1)
                g.pos_shiftf(0.15, 0.0)
                g.rgbcolor(0x666666)
                g.text(n)

        g.rgbcolor(a.controller_app_conf["ui-text-color"])
        g.align("left")
        g.posf(0.6, 0.6)
        g.pos_shiftf(0.0, 0.10)
        g.text("PAGE", 1)
        g.pos_shiftf(0.15, 0.0)
        g.text(a.profile_state["page"], 1)
        g.posf(0.6, 0.6)
        g.pos_shiftf(0.0, 0.15)
        g.text("NOW", 1)
        g.rgbcolor(0xFF4444)
        if str(a.profile_state["page"]) in a.profile_conf["pages"]:
            g.posf(0.6, 0.6)
            g.pos_shiftf(0.15, 0.15)
            if "explanation" in a.profile_conf["pages"][str(a.profile_state["page"])]:
                g.text(a.profile_conf["pages"][str(a.profile_state["page"])]["explanation"])
            else:
                g.text("-----")
            g.posf(0.6, 0.6)
            g.pos_shiftf(0.15, 0.20)
            g.rgbcolor(0x666666)
            if "commands" in a.profile_conf["pages"][str(a.profile_state["page"])]:
                for t in a.profile_conf["pages"][str(a.profile_state["page"])]["commands"].split(sep=";"):
                    g.text(t)
            else:
                g.text("-----")
    
    g.rgbcolor(a.controller_app_conf["ui-text-color"])
    g.box(g.ginfo("sx") * 0.85, g.ginfo("sy") * 0.95 - 2, g.ginfo("sx") * 0.95, g.ginfo("sy") * 0.95 + fontsize + 2)
    g.align("center")
    g.pos(g.ginfo("sx") * 0.9, g.ginfo("sy") * 0.95 + fontsize // 2)
    g.text("PAGE JMP")

    #ACTIVEでなかったときのオーバーレイ警告
    if g.ginfo("act") != 0:
        app_draw_centernotice("*** NOT ACTIVE! ***")
    g.redraw_now()

def app_draw_centernotice(notice_text: str = "") -> None:
        g.align("center")
        g.posf(0.5, 0.5)
        g.color(255, 96, 32)
        g.box(0.35 * g.ginfo("sx"), 0.45 * g.ginfo("sy"), 0.65 * g.ginfo("sx"), 0.55 * g.ginfo("sy"), 2)
        g.text(notice_text)


def app_proc_windowresized(w: int|float, h: int|float) -> None:
    a.controller_app_conf["font-size"] = min((w // 50 + h // 33) // 2, 24)
    app_draw_screen()


def app_proc_tick() -> None:
    if a.controller_app_state["app-lastticktime"] // 250 != time.time_ns() // 1000000 // 250:
        a.controller_app_state["app-tps"] = a.controller_app_state["app-tick-counter"] * 4
        a.controller_app_state["app-tick-counter"] = 0
        if a.controller_app_conf["power-save-mode"] in ["auto", "enabled"]:
            if a.controller_app_state["app-tps"] >= 120:
                a.controller_app_state["power-save-waittime"] += 1
            if a.controller_app_state["app-tps"] <= 75:
                a.controller_app_state["power-save-waittime"] = max(0, a.controller_app_state["power-save-waittime"] - 1)
    a.controller_app_state["app-lastticktime"] = time.time_ns() // 1000000
    a.controller_app_state["app-tick-counter"] += 1

    if "beatdev-lastticktime" not in a.controller_app_state.keys():
        a.controller_app_state["beatdev-lastticktime"] = time.time_ns() // 1000000
    if time.time_ns() // 1000000 - a.controller_app_state["beatdev-lastticktime"] >= 1000 // a.controller_app_conf["fader-tickrate"]:
        a.controller_app_state["beatdev-lastticktime"] = time.time_ns() // 1000000
        a.beatdev_obj.tick()
    
    if "ui-lastdrawtime" not in a.controller_app_state.keys():
        a.controller_app_state["ui-lastdrawtime"] = time.time_ns() // 1000000
    if time.time_ns() // 1000000 - a.controller_app_state["ui-lastdrawtime"] >= 33:
        # UIは約30FPSで動作させる
        a.controller_app_state["ui-lastdrawtime"] = time.time_ns() // 1000000
        app_draw_screen()

    app_brightness_fader_tick()        
    
    if a.controller_app_conf["power-save-mode"] in ["auto", "enabled"]:
        time.sleep(0.0003 * a.controller_app_state["power-save-waittime"])

def app_brightness_fader_tick():
    if a.controller_app_state["brightness"] != a.controller_app_state["brightness-fader-target"]:
        while a.controller_app_state["brightness-fader-lasttime"] <= time.time_ns() // 1000000 + a.controller_app_state["brightness-fader-interval"]:
            if a.controller_app_state["brightness"] == a.controller_app_state["brightness-fader-target"]:
                break
            a.controller_app_state["brightness-fader-lasttime"] += a.controller_app_state["brightness-fader-interval"]
            if a.controller_app_state["brightness"] < a.controller_app_state["brightness-fader-target"]:
                a.controller_app_state["brightness"] += 1
                app_proc_command("NOP")
            if a.controller_app_state["brightness"] > a.controller_app_state["brightness-fader-target"]:
                a.controller_app_state["brightness"] -= 1
                app_proc_command("NOP")
    else:
        a.controller_app_state["brightness-fader-lasttime"] = time.time_ns() // 1000000


def app_proc_keydown(keyunicode: str, keyscancode: int) -> None:
    print("[slf] event KEYDOWN:", keyscancode, keyunicode, "for", a.controller_app_state["key-receiver-function"].__name__)
    a.controller_app_state["key-receiver-function"](keyunicode, keyscancode)
    
    
def keydown_proc_live(keyunicode: str, keyscancode: int) -> None:
    # プロファイルのページキーは決め打ちします
    if keyscancode == 13:
        # J: EVEN
        app_proc_command("PROFILE.PAGE.NEXT_FROM_EVEN")
    elif keyscancode == 15:
        # L: ODD
        app_proc_command("PROFILE.PAGE.NEXT_FROM_ODD")
    else:
        # KEYCONFにヒットするエントリーがあるか検索します
        if keyunicode.upper() in a.keyconf["charcodelist"]:
            # charcode に一致エントリあり
            app_proc_command(a.keyconf["commandlist"][a.keyconf["charcodelist"].index(keyunicode.upper())])
        if keyscancode in a.keyconf["scancodelist"]:
            # scancode に一致エントリあり
            app_proc_command(a.keyconf["commandlist"][a.keyconf["scancodelist"].index(keyscancode)])
        if "key_down_scan" + str(keyscancode) in dir(a.controller_app_conf["keybd-handler"]): 
            getattr(a.controller_app_conf["keybd-handler"], "key_down_scan" + str(keyscancode))(a, app_proc_command)
        elif keyunicode != "" and keyunicode != None:
            # keyboard-handlerクラスに一致エントリあり
            if "key_down_" + str(keyunicode.upper()) in dir(a.controller_app_conf["keybd-handler"]):
                getattr(a.controller_app_conf["keybd-handler"], "key_down_" + str(keyunicode.upper()))(a, app_proc_command)


def app_proc_command(commands: str) -> any:
    for command in commands.strip().split(";"):
        token = str(command).strip().upper().split()
        for tcnt, tk in enumerate(token):
            if tk.startswith("#"):
                #16進数
                token[tcnt] = str(int("0x" + tk[1:], 16))
            if tk == "TRUE":
                token[tcnt] = 1
            if tk == "FALSE":
                token[tcnt] = 0
            if tk == "ON":
                token[tcnt] = 1
            if tk == "OFF":
                token[tcnt] = 0
        targc = len(token) - 1
        if token == [] or token == ["NOP"]:
            pass
        elif token[0].startswith("COLOR."):
            #色に関するコマンド
            if token[0] == "COLOR.TOGGLE":
                if targc == 2:
                    if token[2] not in a.controller_app_conf["light-color"]:
                        a.controller_app_conf["light-color"][token[2]] = int(token[1])
                    else:
                        a.controller_app_conf["light-color"].pop(token[2], None)
                else:
                    print("[proc_command] error with \"" + command + "\"")
            elif token[0] == "COLOR.CLEAR":
                a.controller_app_conf["light-color"] = dict()
            elif token[0] == "COLOR.BLACKOUT.TOGGLE":
                a.controller_app_state["blackout"] = (a.controller_app_state["blackout"] + 1) % 2
                if a.controller_app_state["blackout"] == 1:
                    #OFF
                    a.primdev_obj.stoppattern()
                else:
                    #ON
                    a.primdev_obj.startpattern()
            elif token[0] == "COLOR.BLACKOUT.SET":
                a.controller_app_state["blackout"] = int(token[1]) % 2
                if a.controller_app_state["blackout"] == 1:
                    #OFF
                    a.primdev_obj.stoppattern()
                else:
                    #ON
                    a.primdev_obj.startpattern()
            elif token[0] == "COLOR.BRIGHTNESS.SETTARGET":
                a.controller_app_state["brightness-fader-target"] = int(token[1]) % 256
            elif token[0] == "COLOR.BRIGHTNESS.SETINTERVAL":
                a.controller_app_state["brightness-fader-interval"] = int(token[1])
            else:
                g.logmes("[slf] Unknown command " + token[0], 2)
        elif token[0].startswith("BPM."):
            #BPMに関するコマンド
            if token[0] == "BPM.SET":
                a.beatdev_obj.bpm = float(token[1])
            elif token[0] == "BPM.INCREASE":
                a.beatdev_obj.bpm += float(token[1])
            elif token[0] == "BPM.DECREASE":
                a.beatdev_obj.bpm -= float(token[1])
            elif token[0] == "BPM.DOUBLE":
                a.beatdev_obj.bpm *= 2
            elif token[0] == "BPM.HALF":
                a.beatdev_obj.bpm //= 2
            else:
                g.logmes("[slf] Unknown command " + token[0], 2)
        elif token[0].startswith("BEATS."):
            if token[0] == "BEATS.SET":
                a.beatdev_obj.beats = int(token[1])
            elif token[0] == "BEATS.ALIGN":
                a.beatdev_obj.reset_time(4.0 + a.beatdev_obj.currstamp // 4 * 4 - 0.01)
            else:
                g.logmes("[slf] Unknown command " + token[0], 2)
        elif token[0].startswith("PATTERN."):
            if token[0] == "PATTERN.BANK.SET":
                a.controller_app_state["primary-bank"] = int(token[1])
                #a.primdev_obj.stoppattern()
                a.primdev_obj.bankset(a.controller_app_state["primary-bank"])
                a.primdev_obj.startpattern()
            elif token[0] == "PATTERN.FADER.SET":
                a.controller_app_state["primary-fader"] = decimal.Decimal(token[1])
            elif token[0] == "PATTERN.FADER.INCREASE":
                # 0.1 + 0.2 = 0.30000000004になるのでしゃーなしでDecimal型を使う
                a.controller_app_state["primary-fader"] += decimal.Decimal(token[1])
            elif token[0] == "PATTERN.FADER.DECREASE":
                a.controller_app_state["primary-fader"] -= decimal.Decimal(token[1])
            else:
                g.logmes("[slf] Unknown command " + token[0], 2)
        elif token[0].startswith("PROFILE."):
            if token[0] == "PROFILE.PAGE.NEXT_FROM_EVEN":
                if a.profile_state["page"] % 2 == 0 and a.profile_state["avail"] == 1:
                    if str(a.profile_state["page"]) in a.profile_conf["pages"]:
                        if "next_page" in a.profile_conf["pages"][str(a.profile_state["page"])]:
                            a.profile_state["page"] = int(a.profile_conf["pages"][str(a.profile_state["page"])]["next_page"])
                            app_proc_command("PROFILE.PAGE.APPLY")
            elif token[0] == "PROFILE.PAGE.NEXT_FROM_ODD":
                if a.profile_state["page"] % 2 == 1 and a.profile_state["avail"] == 1:
                    if str(a.profile_state["page"]) in a.profile_conf["pages"]:
                        if "next_page" in a.profile_conf["pages"][str(a.profile_state["page"])]:
                            a.profile_state["page"] = int(a.profile_conf["pages"][str(a.profile_state["page"])]["next_page"])
                            app_proc_command("PROFILE.PAGE.APPLY")
            elif token[0] == "PROFILE.PAGE.APPLY":
                if "pages" in a.profile_conf:
                    if str(a.profile_state["page"]) in a.profile_conf["pages"]:
                        if "commands" in a.profile_conf["pages"][str(a.profile_state["page"])]:
                            app_proc_command(a.profile_conf["pages"][str(a.profile_state["page"])]["commands"])
                else:
                    a.profile_state["avail"] = 0
                    g.logmes("[slf] ERROR when applying profile page! Profile Mode Disabled")
            elif token[0] == "PROFILE.ASKPAGENUM":
                ip = tkinter.simpledialog.askinteger("profile.askpagenum", "page number? :", minvalue = 0)
                if ip != None:
                    a.profile_state["page"] = ip
                    app_proc_command("PROFILE.PAGE.APPLY")
            else:
                g.logmes("[slf] Unknown command " + token[0], 2)
        elif token[0] == "CONSOLE":
                command = tkinter.simpledialog.askstring("console", "Command? :", initialvalue="")
                if command != None:
                    app_proc_command(command)
                command = ""
        else:
            g.logmes("[slf] Unknown command " + token[0], 2)
        a.controller_app_state["primary-fader"] = max(decimal.Decimal(0.0), a.controller_app_state["primary-fader"])
        a.primdev_obj.faderset(float(a.controller_app_state["primary-fader"]))
        cks = []
        for ck in list(a.controller_app_conf["light-color"].values()):
            cks.append(cb2v(ck, a.controller_app_state["brightness"]))
        a.primdev_obj.colorset(cks)
    if a.controller_app_state["blackout"] == 1:
        a.primdev_obj.stoppattern()

def cb2v(color: int = 0, brightness: int = 255) -> int:
    return (
        (color // 65536 * brightness // 255) * 65536
    +   (color % 65536 // 256 * brightness // 255) * 256
    +   (color % 256 * brightness // 255) * 1
    )


def primarysetter(device_name: str, param_name: str, color: int, fader: int|float) -> None:
    if device_name not in [_["name"] for _ in a.logidev_conf]:
        g.logmes("[WARN] primarysetter: Could not find device \"" + str(device_name) + "\"", 1)
        return None
    devid = [_["name"] for _ in a.logidev_conf].index(device_name)
    if a.logidev_obj[devid] == None:
        g.logmes("[WARN]: primarysetter: Device \"" + str(device_name) + "\" is invalid", 1)
        return None
    if param_name not in a.logidev_obj[devid].paramlist():
        g.logmes("[WARN]: primarysetter: Could not find parameter \"" + str(param_name) + "\" in device \"" + str(device_name) + "\"", 1)
        return None
    for fdk, fdv in a.logidev_obj[devid].set(param_name, color, fader).items():
        a.beatdev_obj.register_fader(a.physidev_obj.set, a.physidev_obj.get, int(fdk), int(fdv["value"]), float(fdv["fade"]))


def app_proc_mbuttondown(mx: int|float, my: int|float) -> None:
    if g.ginfo("sx") * 0.85 <= mx <= g.ginfo("sx") * 0.95 and g.ginfo("sy") * 0.6 - 2 < my < g.ginfo("sy") * 0.6 + a.controller_app_conf["font-size"] + 2:
        #プロファイルのロードボタン
        fn = tkinter.filedialog.askopenfilename()
        if fn != "":
            app_draw_centernotice("Loading!")
            g.redraw_now()
            with open(fn, encoding = "utf-8") as fobj:
                if fobj != None:
                    try:
                        a.profile_conf = json.loads(fobj.read())
                    except Exception as e:
                        #UnicodeDecodeError, json.decoder.JSONDecodeError
                        g.logmes("[slf] ERROR: A trouble when loading \"" + str(fn) + "\" : " + str(e) + ", " + str(type(e)))
                        a.profile_state["avail"] = 0
                    else:
                        a.profile_state["avail"] = 1
                        a.profile_state["filename"] = fn
                        a.profile_state["page"] = 0
                        a.profile_state["screenname"] = a.profile_conf["profile_name"] if "profile_name" in a.profile_conf else os.path.splitext(os.path.basename(fn))[0]
                        app_proc_command("PROFILE.PAGE.APPLY")
    if g.ginfo("sx") * 0.85 <= mx <= g.ginfo("sx") * 0.95 and g.ginfo("sy") * 0.95 - 2 < my < g.ginfo("sy") * 0.95 + a.controller_app_conf["font-size"] + 2:
        app_proc_command("profile.askpagenum")
                    

#main
if __name__ == "__main__":
    if sys.version_info.major != 3 or sys.version_info.minor <= 9:
        print("This program will not work on Python 3.9 or below! Please install newer version of Python3.")
        print("このプログラムはPython 3.9以下では動作しません! より新しいバージョンのPython3をインストールしてください。")
        sys.exit(-1)
    errorflag = 0
    a = lfapp_struct()
    a.controller_app_conf = {"font-size": 16, "light-color": dict(), "ui-background-color": 2236962, "ui-text-color": 15658734, "fader-tickrate": 20, "power-save-mode": "auto"}
    a.controller_app_state["app-lastticktime"] = 0
    a.controller_app_state["app-tps"] = 0
    a.controller_app_state["app-tick-counter"] = 0
    a.controller_app_state["blackout"] = 1
    a.controller_app_state["primary-bank"] = 0
    a.controller_app_state["primary-fader"] = decimal.Decimal(0.5)
    a.controller_app_state["power-save-waittime"] = 0
    a.controller_app_state["brightness"] = 255
    a.controller_app_state["brightness-fader-target"] = 255
    a.controller_app_state["brightness-fader-lasttime"] = 0
    a.controller_app_state["brightness-fader-interval"] = 20
    a.controller_app_state["key-receiver-function"] = keydown_proc_live
    a.controller_app_state["drawer-function"] = None
    # ↑ 100msあたりの変化量
    g = sgpg.sgpg()
    g.screen(0, 800, 500, 32)
    g.title("Light Controller v0.1")
    print("本ソフトウェアはフォント「IPAexゴシック」を使用しています。IPAexゴシックの利用には、IPAフォントライセンスv1.0に同意する必要があります。詳しくは IPA_Font_License_Agreement_v1.0.txt をご覧ください。")
    app_init()
    g.stop()

