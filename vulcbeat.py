import time
import math

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
class beatmanager():
    """VULC beat-manager class"""
    def __init__(self, bpm: int|float = 120, beats: int = 4):
        """

        Args:
            bpm (int|float): BPM(Optional, Default: 120).
            beats (int): Beat(Optional, Default: 4).

        """
        self.bpm = float(bpm)
        self.beats = beats
        self._timestamp = time.time_ns() // 1000
        self.beatstamp = [0, -0.1]
        self.prevstamp = 0.0
        self.currstamp = 0.0
        # tsclbk : {time_signature: callback}
        self.tsclbk = dict()
        # faderclbk : {channel: [setter, getter, current_value, purpose_value, time_set, time_ellapsed]}
        self.faderclbk = dict()
# ------------------------------------------------------------------------------------------------
    def set_callback_on_beat(self, timing: int|float, callback: callable) -> None:
        """Set callback for specified timing.

        Do not call this method in callback method.

        Args:
            timing (int): the beat signature to call callback.
            callback (callable): the callback method.

        Returns:
            None.
        """
        self.tsclbk.update({timing: callback})
# ------------------------------------------------------------------------------------------------
    def clear_all_callback_on_beat(self) -> None:
        """Clear all callback for specified timing.

        Do not call this method in callback method.

        Args:
            None.

        Returns: 
            None.
        """
        self.tsclbk = dict()
# ------------------------------------------------------------------------------------------------
    def register_fader(self, setter: callable, getter: callable, channel: int, value: int, transition_time: float = 0.0):
        """Register new fader.

        Register new fader which is to set the value of one specified channel 
        to specified number in specified transition time.
        Faders' procedure is run at tick method.
        The fader will be deleted if its transition time is exceeded.
        New registration to the same channel will cause override.

        Args:
            setter (callable): set method of Raw-Controller for fader.
            getter (callable): get method of Raw-Controller for fader.
            channel (int): channel number to apply the fader.
            value (int): purpose value of the fader.
            transition_time (float): length of the beat signature for the fader to move the value from current number to the the purpose.

        Returns:
            None.

        """
        self.faderclbk.update({channel: [setter, getter, getter(channel), value, transition_time, 0.0]})
# ------------------------------------------------------------------------------------------------
    def clear_all_fader(self) -> None:
        """Clear all fader. the value-change event will never appear.

        Args:
            None.
        Returs:
            None.
        """
        self.faderclbk = dict()
# ------------------------------------------------------------------------------------------------
    def reset_time(self, reset_value : int|float = 0.0):
        self.beatstamp[0] = math.floor(reset_value)
        self.beatstamp[1] = reset_value - math.floor(reset_value)
        self._timestamp = time.time_ns() // 1000
# ------------------------------------------------------------------------------------------------
    def tick(self) -> None:
        """Run sets of time procedure for 1 time.

        These are procedures in this method:
            * Get current time, then calculate beatstamp.
            * Compare calculated beatstamp with previous one to determine which callback method is called.
            * Execute fader procedures and set appropriate value.
        
        Args:
            None.

        Returns:
            None.
        """
        self.bpm = max(1.0, self.bpm)
        self.beats = max(1, self.beats)
        self.prevstamp = float(self.beatstamp[0]) + self.beatstamp[1]
        self.newtime = time.time_ns() // 1000
        self.beatstamp[1] += float(self.newtime - self._timestamp) / (60000000 / self.bpm)
        self._timestamp = self.newtime
        if self.beatstamp[1] >= 1.0:
            self.beatstamp[0] += int(self.beatstamp[1] // 1.0)
            self.beatstamp[1] = self.beatstamp[1] % 1.0
        #
        self.currstamp = float(self.beatstamp[0]) + self.beatstamp[1]
        #
        if self.prevstamp != self.currstamp:
            stampdiff = self.currstamp - self.prevstamp
            # Callback
            for i in self.tsclbk.keys():
                if (self.currstamp - i) // self.beats != (self.prevstamp - i) // self.beats:
                    self.tsclbk[i](round(self.currstamp, 3))
            # Fader
            dellist = []
            for f in self.faderclbk:
                self.faderclbk[f][5] = min(self.faderclbk[f][4], self.faderclbk[f][5] + stampdiff)
                if self.faderclbk[f][4] != 0.0:
                    newv = self.faderclbk[f][2] + (self.faderclbk[f][3] - self.faderclbk[f][2]) * self.faderclbk[f][5] / self.faderclbk[f][4]
                else:
                    newv = self.faderclbk[f][3]
                self.faderclbk[f][0](f, newv)
                if self.faderclbk[f][5] >= self.faderclbk[f][4]:
                    dellist.append(f)
            for L in dellist:
                self.faderclbk.pop(L)
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
"""
def beatL(timestamp):
    print("L", timestamp)
    a.register_fader(drv.set, drv.get, 96, 255, 0.05)
    a.register_fader(drv.set, drv.get, 97,   0, 0.05)
def beatR(timestamp):
    print("R", timestamp)
    a.register_fader(drv.set, drv.get, 96,   0, 0.05)
    a.register_fader(drv.set, drv.get, 97, 255, 0.05)

v = 0
def testgetter(channel):
    global v
    print("get", channel, v)
    return v
def testsetter(channel, value):
    global v
    print("set", channel, value)
    v = value

import importlib

drvsrc = importlib.import_module("abdmxraw")

drv = drvsrc.physical_driver(portnum = -1)

a = beatmanager(bpm=125, beats=4)
a.set_callback_on_beat(0.0, beatL)
a.set_callback_on_beat(1.0, beatR)
a.set_callback_on_beat(2.0, beatL)
a.set_callback_on_beat(3.0, beatR)
c = 0
while True:
    if a.beatstamp[0] > c:
        c = a.beatstamp[0]
    if a.currstamp >= 8:
        a.reset_time(0.5)
    a.tick()
"""


"""
while True:
    if a.currstamp >= 8 and c == 0:
        c = 1
        a.register_fader(drv.set, drv.get, 96, 255, 0.5)
        a.register_fader(drv.set, drv.get, 99, 255, 0.5)
        a.register_fader(drv.set, drv.get, 102, 255, 0.5)
        a.register_fader(drv.set, drv.get, 105, 255, 0.5)
    if a.currstamp >= 12 and c == 1:
        c = 2
        a.register_fader(drv.set, drv.get, 96, 0, 2.0)
        a.register_fader(drv.set, drv.get, 99, 0, 2.0)
        a.register_fader(drv.set, drv.get, 102, 0, 2.0)
        a.register_fader(drv.set, drv.get, 105, 0, 2.0)
    if a.currstamp >= 4:
        a.bpm = 120.0
    a.tick()
"""