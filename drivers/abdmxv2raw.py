import serial
import time
import serial.tools.list_ports
import serial.serialutil
from typing import Callable

class physical_driver:
    def __init__(self, option: dict, loggermethod: Callable | None = None) -> None:
        self.chval = [0] * 256
        portnum = option["port"]
        self.port = serial.Serial()
        self.logoutput = 0
        if portnum != -1:
            try:
                self.port = serial.Serial(port="COM" + str(portnum), baudrate=38400, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
                self.portnumber = portnum
            except serial.serialutil.SerialException as e:
                if loggermethod != None:
                    loggermethod("[abdmxv2raw] Failed to open " + str(portnum), 1)
                    loggermethod("[abdmxv2raw] Hint: Available Ports are: " + ", ".join([_.device for _ in serial.tools.list_ports.comports()]))
                else:
                    print("[abdmxv2raw] Failed to open COM" + str(portnum))
                    print("[abdmxv2raw] Hint: Available Ports are: ", [_.device for _ in serial.tools.list_ports.comports()])
                self.portnumber = -1
        else:
            self.portnumber = -1
            self.logoutput = 0
    def set(self, channel: int, value: int) -> None:
        if self.chval[channel] != int(value):
            if self.logoutput == 1:
                print("[abdmxv2raw] set", channel, int(value))
            self.chval[channel] = int(value)
            if self.portnumber != -1:
                self.port.write(bytearray([int(channel) % 128, int(value) % 256 // 2 + 128]))
        else:
            if self.logoutput == 1:
                print("[abdmxv2raw] set", channel, int(value), "(skip)")
    def get(self, channel: int) -> int:
        if self.logoutput == 1:
            print("[abdmxv2raw] get", channel)
        return self.chval[channel]
    def isremotecontroller(self) -> bool:
        if self.portnumber == -1:
            return False
        else:
            return True
