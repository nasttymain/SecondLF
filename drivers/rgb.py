# memo: 装置固有デバイスドライバではフェーダーパラメータは通常扱わず、より高位のプライマリデバイスドライバが設定を行う想定になっている。
class light_driver:
    def __init__(self, mode: list, option: dict) -> None:
        self.chm = mode
        self.color = 0
    def reset(self) -> dict:
        self.color = 0
        return {
            self.chm[0] + 0 : {"value": 0, "fade": 0.0},
            self.chm[0] + 1 : {"value": 0, "fade": 0.0},
            self.chm[0] + 2 : {"value": 0, "fade": 0.0},
        }
    def close(self) -> dict:
        return dict()
    def info(self) -> str:
        return "(C)2023 /\/asTTY\ngeneral RGB LED driver."
    def apiver(self) -> int:
        return 1
    def displayparam(self) -> list:
        return [
            {
                "category": "color.rgb",
                "type": "int",
                "value": self.color,
                "alloc": self.chm[0]
            }
        ]
    def paramlist(self) -> list:
        return ["color"]
    def set(self, param_name: str, value: int|float, fader: int|float) -> dict:
        if param_name == "color":
            self.color = value
            return {
                self.chm[0] + 0 : {"value": value // 65536,       "fade": fader},
                self.chm[0] + 1 : {"value": value % 65536 // 256, "fade": fader},
                self.chm[0] + 2 : {"value": value % 256,          "fade": fader},
            }
        else:
            return dict()
    def get(self, param_name: str) -> any:
        if param_name == "color":
            return self.color
        else:
            return None
