import serial
import time
import serial.tools.list_ports
import serial.serialutil

class physical_driver:
    def __init__(self, option: dict, loggermethod: callable = None) -> None:
        self.chval = [None] * 256
        portnum = option["port"]
        self.port = None
        self.logoutput = 0
        if portnum != -1:
            try:
                self.port = serial.Serial(port="COM" + str(portnum), baudrate=38400, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
                self.portnumber = portnum
            except serial.serialutil.SerialException as e:
                if loggermethod != None:
                    loggermethod("[abdmxraw] Failed to open " + str(portnum), 1)
                    loggermethod("[abdmxraw] Hint: Available Ports are: " + ", ".join([_.device for _ in serial.tools.list_ports.comports()]))
                else:
                    print("[abdmxraw] Failed to open COM" + str(portnum))
                    print("[abdmxraw] Hint: Available Ports are: ", [_.device for _ in serial.tools.list_ports.comports()])
                self.portnumber = -1
        else:
            self.portnumber = -1
            self.logoutput = 0
    def set(self, channel: int, value: int) -> None:
        if self.chval[channel] != int(value):
            if self.logoutput == 1:
                print("[abdmxraw] set", channel, int(value))
            self.chval[channel] = int(value)
            if self.portnumber != -1:
                checksum = (int(channel) % 16 + int(channel) // 16 + int(value) % 16 + int(value) // 16) % 16
                self.port.write(bytearray([checksum, int(channel), int(value)]))
                #time.sleep(0.01)
        else:
            if self.logoutput == 1:
                print("[abdmxraw] set", channel, int(value), "(skip)")
    def get(self, channel: int) -> int:
        if self.logoutput == 1:
            print("[abdmxraw] get", channel)
        return self.chval[channel]
    def isremotecontroller(self) -> bool:
        if self.portnumber == -1:
            return False
        else:
            return True
