import os.path
import random
import json
class primary_driver:
    def __init__(self, beat_device_object: object) -> None:
        self.program_bank = 0
        self.fader = 0.0
        self.color = []
        self.colorsel = 0
        self.currentcolor = 0
        self.callback = None
        self.beatdev_obj = beat_device_object
        self.specialattr = 0
        self.listattr = []

        self.colorslist = [
            ["LED L-L", "color"],
            ["LED L-R", "color"],
            ["LED R-L", "color"],
            ["LED R-R", "color"],
            ["TSIG L", "color1"],
            ["TSIG L", "color2"],
            ["TSIG L", "color3"],
            ["TSIG L", "color4"],
            ["TSIG R", "color1"],
            ["TSIG R", "color2"],
            ["TSIG R", "color3"],
            ["TSIG R", "color4"],
            ["DEKKER", "color"],
        ]
        self.pattern7_shifttime = 7

        if not os.path.isfile("drivers/primaryconf.json"):
            print("[primary] WARNING: Could not find primaryconf.json! The primary driver will not work properly.")
        else:
            with open("drivers/primaryconf.json", mode="r") as f:
                fj = json.load(f)
                if "rgbleds" in fj.keys():
                    if type(fj["rgbleds"]) is list:
                        #print(fj["rgbleds"])
                        self.colorslist = fj["rgbleds"]
    def apiver(self) -> int:
        return 1
    def info(self) -> str:
        return "(C)2023 /\\/asTTY\nThe primary driver.\nUse primaryconf.json to add/remove devices and change actions."
    def bankinfo(self) -> str:
        sl = [
            "0 F1 2022互換",
            "1 F2 2022互換 - ミラーのみ",
            "2 F3 2022互換 - オールオン",
            "3 F4 色点滅",
            "4 F5 ポリゴンショック",
            "5 F6 ランダムタイミング・ランダムカラー",
            "6 F7 2拍・ランダムカラー",
            "7 F8 ランダムフェーズ・シーケンスカラー"
            "8 (割当無) 1拍毎に左右(May 2024)"
        ]
        if self.program_bank < len(sl):
            return sl[self.program_bank]
        else:
            return ""
    def bankset(self, bank: int) -> None:
        self.program_bank = bank
    def faderset(self, fader: int|float) -> None:
        self.fader = fader
    def colorset(self, colorlist: list) -> None:
        self.color = colorlist
    def actionclbkset(self, callback: callable) -> None:
        self.callback = callback
    def startpattern(self) -> None:
        self.beatdev_obj.clear_all_callback_on_beat()
        if self.program_bank in [0, 1, 2]:
            # 2022、MIRROR、ALLON
            for t in range(4):
                self.beatdev_obj.set_callback_on_beat(float(t), self.timing_callback)
        elif self.program_bank in [3, 4]:
            # FLASH POLYGON
            for t in [tn * 0.2 for tn in range(0, 20)]:
                self.beatdev_obj.set_callback_on_beat(t, self.timing_callback)
        elif self.program_bank in [5]:
            # RANDOM
            self.listattr = [0 for _ in self.colorslist]
            for t in [tn * 0.5 for tn in range(0, 8)]:
                self.beatdev_obj.set_callback_on_beat(t, self.timing_callback)
            if self.color != []:
                for cl in self.colorslist:
                    self.callback(cl[0], cl[1], random.sample(self.color, k = 1)[0], 0.0)
        elif self.program_bank in [6]:
            # BEAT 1 & 3
            for t in range(0, 4, 2):
                self.beatdev_obj.set_callback_on_beat(t, self.timing_callback)
        elif self.program_bank in [7]:
            # RANDOM ROUND
            for t in [tn * 0.2 for tn in range(0, 20)]:
                self.beatdev_obj.set_callback_on_beat(t, self.timing_callback)
            if self.color == []:
                self.listattr = [[0, 0] for _ in self.colorslist]
            else:
                self.listattr = [[random.randint(0, len(self.color) - 1), random.randint(0, self.pattern7_shifttime - 1)] for _ in self.colorslist]
        elif self.program_bank in [8]:
            # 左右
            for t in range(4):
                self.beatdev_obj.set_callback_on_beat(float(t), self.timing_callback)

            
        pass
    def stoppattern(self) -> None:
        self.beatdev_obj.clear_all_callback_on_beat()

        for cl in self.colorslist:
            self.callback(cl[0], cl[1], 0, 0.0)
        pass

    def timing_callback(self, timestamp) -> None:
        if self.program_bank == 0:
            # Keion 2022
            if len(self.color) == 0:
                self.currentcolor = 0
            else:
                if int(timestamp) % 4 == 0:
                    # bar
                        self.colorsel += 1
                if self.colorsel >= len(self.color):
                    self.colorsel = 0
                self.currentcolor = self.color[self.colorsel]

            for cl in self.colorslist:
                if not cl[0].startswith("TSIG"):
                    self.callback(cl[0], cl[1], self.currentcolor, self.fader)

            if int(timestamp) % 2 == 0:
                # Left
                self.callback("TSIG L", "color1", self.currentcolor, self.fader)
                self.callback("TSIG L", "color2",                 0, self.fader)
                self.callback("TSIG L", "color3", self.currentcolor, self.fader)
                self.callback("TSIG L", "color4",                 0, self.fader)
                self.callback("TSIG R", "color1", self.currentcolor, self.fader)
                self.callback("TSIG R", "color2",                 0, self.fader)
                self.callback("TSIG R", "color3", self.currentcolor, self.fader)
                self.callback("TSIG R", "color4",                 0, self.fader)
            else: 
                # Right
                self.callback("TSIG L", "color2", self.currentcolor, self.fader)
                self.callback("TSIG L", "color1",                 0, self.fader)
                self.callback("TSIG L", "color4", self.currentcolor, self.fader)
                self.callback("TSIG L", "color3",                 0, self.fader)
                self.callback("TSIG R", "color2", self.currentcolor, self.fader)
                self.callback("TSIG R", "color1",                 0, self.fader)
                self.callback("TSIG R", "color4", self.currentcolor, self.fader)
                self.callback("TSIG R", "color3",                 0, self.fader)
        elif self.program_bank == 1:
            # MIRROR ONLY
            if len(self.color) == 0:
                self.currentcolor = 0
            else:
                if int(timestamp) % 4 == 0:
                    # bar
                        self.colorsel += 1
                if self.colorsel >= len(self.color):
                    self.colorsel = 0
                self.currentcolor = self.color[self.colorsel]

            for cl in self.colorslist:
                if cl[0] != "DEKKER":
                    self.callback(cl[0], cl[1],  0, self.fader)
            self.callback("DEKKER", "color",  self.currentcolor, self.fader)
        elif self.program_bank == 2:
            # All on
            if len(self.color) == 0:
                self.currentcolor = 0
            else:
                if int(timestamp) % 4 == 0:
                    # bar
                        self.colorsel += 1
                if self.colorsel >= len(self.color):
                    self.colorsel = 0
                self.currentcolor = self.color[self.colorsel]
            
            for cl in self.colorslist:
                self.callback(cl[0], cl[1],  self.currentcolor, self.fader)
        elif self.program_bank == 3:
            if len(self.color) == 0:
                self.currentcolor = 0
            else:
                if int(timestamp * 10) % 40 == 0:
                    # bar
                        self.colorsel += 1
                if self.colorsel >= len(self.color):
                    self.colorsel = 0
                self.currentcolor = self.color[self.colorsel]
            self.specialattr = (self.specialattr + 1) % 2
            for cl in self.colorslist:
                if self.specialattr == 0:
                    self.callback(cl[0], cl[1],                  0, 0.0)
                else:
                    self.callback(cl[0], cl[1],  self.currentcolor, 0.0)
        elif self.program_bank == 4:
            if len(self.color) == 0:
                self.currentcolor = 0
            else:
                self.colorsel += 1
                if self.colorsel >= len(self.color):
                    self.colorsel = 0
                self.currentcolor = self.color[self.colorsel]
            for cl in self.colorslist:
                self.callback(cl[0], cl[1],  self.currentcolor, 0.0)
        elif self.program_bank == 5:
            for cl in self.colorslist:
                self.callback(cl[0], cl[1], 0, self.fader * 7)
            if self.color != []:
                """
                for ct in random.sample(self.colorslist, k = min(4, len(self.colorslist))):
                    cc = random.sample(self.color, k = 1)[0]
                    self.callback(ct[0], ct[1], cc, (0.1 if self.fader >= 0.1 else 0.0))
                """
                cl = 0
                for acnt, attr in enumerate(self.listattr):
                    if attr <= 0:
                        self.listattr[acnt] = random.randint(1, 4)
                        if random.random() > 0.6:
                            cc = self.color[int(timestamp) // 4 % len(self.color)]
                        else:
                            cc = random.sample(self.color, k = 1)[0]

                        self.callback(self.colorslist[acnt][0], self.colorslist[acnt][1], cc, (0.0 if self.fader == 0.0 else self.fader / 4))
                        cl += 1
                    else:
                        self.listattr[acnt] -= 1
        elif self.program_bank == 6:
            if self.color == []:
                for cl in self.colorslist:
                    self.callback(cl[0], cl[1], 0, self.fader)
            else:
                for clcnt, cl in enumerate(random.sample(self.colorslist, len(self.colorslist))):
                    self.callback(cl[0], cl[1], self.color[clcnt % len(self.color)], self.fader)
        elif self.program_bank == 7:
            if self.color == []:
                for cl in self.colorslist:
                    self.callback(cl[0], cl[1], 0, self.fader)
            else:
                for clcnt, cl in enumerate(self.listattr):
                    if cl[1] <= 0:
                        self.listattr[clcnt][0] += 1
                        if self.listattr[clcnt][0] >= len(self.color):
                            self.listattr[clcnt][0] = 0
                        r = [
                            int(self.pattern7_shifttime * (0.5 + self.fader * 0.5)),
                            int(self.pattern7_shifttime * (0.5 + self.fader * 0.5)),
                            int(self.pattern7_shifttime * (0.5 + self.fader * 0.5)),
                            int(self.pattern7_shifttime * (0.5 + self.fader * 0.5)),
                            int(self.pattern7_shifttime * (0.5 + self.fader * 0.5)),
                            int(self.pattern7_shifttime * (0.5 + self.fader * 0.5)) + 1,
                            int(self.pattern7_shifttime * (0.5 + self.fader * 0.5)) - 1
                        ]
                        self.listattr[clcnt][1] = random.choice(r)
                        self.callback(self.colorslist[clcnt][0], self.colorslist[clcnt][1], self.color[self.listattr[clcnt][0]], 0.1 + self.fader * 0.5)
                    else:
                        self.listattr[clcnt][1] -= 1
                        if cl[1] <= 1:
                            self.callback(self.colorslist[clcnt][0], self.colorslist[clcnt][1], 0, self.fader * self.pattern7_shifttime)
        elif self.program_bank == 8:
            if self.color == []:
                for cl in self.colorslist:
                    self.callback(cl[0], cl[1], 0, self.fader)
            else:
                for clcnt, cl in enumerate(random.sample(self.colorslist, len(self.colorslist))):
                    left = [
                    "LED L-L",
                    "LED L-R",
                    "LED L-F",
                    "LED L-FL",
                    "TSIG L",
                    "TSIG L",
                    "TSIG L",
                    "TSIG L",
                    ]
                    if cl[0] == "DEKKER":
                            self.callback(cl[0], cl[1], 0, self.fader)
                    elif (int(timestamp) % 2 == 0 and cl[0] in left) or (int(timestamp) % 2 != 0 and cl[0] not in left):
                            self.callback(cl[0], cl[1], self.color[int(timestamp) % len(self.color)], self.fader)
                    else:
                            self.callback(cl[0], cl[1], 0, self.fader)
                        