from pygame.time import get_ticks, wait

class Timer:
    def __init__(self, period: float):
        """
        Make a repeatable timer with a set period, in seconds.
        """
        self.period_ms = period * 1000
        self.time_last = 0
    
    def wait(self):
        time_now = get_ticks()
        dt = time_now - self.time_last
        if (dt < self.period_ms):
            wait(int(self.period_ms - dt))
            self.time_last = time_now + self.period_ms
        else:
            self.time_last = time_now
