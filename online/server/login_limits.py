"""Bounded, monotonic in-memory attempt limiter for loopback prototype."""
import time

class AttemptLimiter:
    def __init__(self, limit=5, window=300, clock=None, capacity=4096):
        self.limit=limit
        self.window=window
        self.clock=clock or time.monotonic
        self.capacity=capacity
        self.events={}
    def _key(self, username):
        if not isinstance(username,str) or not 1<=len(username)<=24:
            return "invalid-name"
        return username.casefold()
    def blocked(self, username):
        key=self._key(username)
        self._prune(key)
        return len(self.events.get(key,()))>=self.limit
    def failure(self, username):
        key=self._key(username)
        self._prune(key)
        if key not in self.events and len(self.events)>=self.capacity:
            # Fail closed when the in-memory limiter has reached capacity.
            return False
        self.events.setdefault(key,[]).append(self.clock())
        return True
    def success(self, username):
        self.events.pop(self._key(username),None)
    def _prune(self,key):
        now=self.clock()
        if key in self.events:
            fresh=[t for t in self.events[key] if now-t<self.window]
            if fresh:self.events[key]=fresh
            else:self.events.pop(key,None)
        # Opportunistically free expired entries globally.
        if len(self.events)>=self.capacity:
            for other in list(self.events):
                if other!=key:
                    fresh=[t for t in self.events[other] if now-t<self.window]
                    if fresh:self.events[other]=fresh
                    else:self.events.pop(other,None)
    def saturated(self):
        self._prune("invalid-name")
        return len(self.events)>=self.capacity
