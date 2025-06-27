RGB = (0, 1, 2)
RBG = (0, 2, 1)
BGR = (2, 1, 0)
RED = (31, 0, 0)
GREEN = (0, 31, 0)
BLUE = (0, 0, 31)
ORANGE = (31, 15, 0)
YELLOW = (31, 31, 0)
LIGHTGREEN = (15, 31, 0)
LIGHTBLUE = (0, 31, 31)
PURPLE = (31, 0, 31)

import serial
import serial.tools.list_ports
class LEDArray(object):
    def __init__(self) -> None:
        self.rgbtype: tuple[int, int, int] = (0, 1, 2)
        self.count: int = 100
        self.style: int = 1
        self.buffer: list[int] = []
        self.mdimmer: float = 0.05
        self.port: serial.Serial = serial.Serial()
        pass

    def __color(self, r: int, g: int, b: int, m: float) -> int:
        _cols = (r, g, b)
        return int(_cols[self.rgbtype[0]] * m) * 1024 + int(_cols[self.rgbtype[1]] * m) * 32 + int(_cols[self.rgbtype[2]] * m)
    
    def set_colors(self, colors : list[tuple[int, int, int]]) -> None:
        self.buffer = [0x88, 0x00]
        for c in colors:
            cv = self.__color(c[0], c[1], c[2], self.mdimmer)
            self.buffer.append(cv // 256)
            self.buffer.append(cv % 256)
        self.buffer.append(0x98)
        self.buffer.append(0x00)
    
    def __send_bytes(self, data: bytearray) -> None:
        try:
            self.port.write(data)
        except Exception as e:
            #print(e)
            ...

    def send_colors(self) -> None:
        self.__send_bytes(bytearray(self.buffer))

    def send_reset(self) -> None:
        self.__send_bytes(bytearray([0xFF, 0xFF, 0xFF, 0xFF]))

    def send_clear(self) -> None:
        self.__send_bytes(bytearray([0x88, 0x00, 0x98, 0x00]))

    def avail_ports(self) -> list[str]:
        return [_.device for _ in serial.tools.list_ports.comports()]

if __name__ == "__main__":
    import time
    arrobj = LEDArray()
    arrobj.rgbtype = RBG
    arrobj.port = serial.Serial()
    arrobj.port.port = "COM5"
    arrobj.port.open()
    arrobj.send_reset()
    col = ([(31, 31, 31)] * 99)
    col.append((0, 31, 0))
    while True:
        arrobj.set_colors(col)
        arrobj.send_colors()
        time.sleep(0.1)
